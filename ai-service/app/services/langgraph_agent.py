import os
import pymysql
from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.vectordb.chroma import get_vector_store
from app.services.sql_agent import query_mysql, get_db_connection
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    question: str
    user: Optional[Dict[str, Any]]
    history: Optional[List[Dict[str, str]]]
    agent_chosen: str       # "RAG", "SQL", "HYBRID", "BLOCKED"
    rag_context: str
    rag_docs: List[str]
    sql_result: Any
    sql_query: str
    answer: str
    status: str             # "Allowed", "Denied", "Success", "Fallback", "Blocked"
    retries: int

def log_audit_entry(state: AgentState):
    """Step 7: Log every action into MySQL audit_logs table."""
    conn = None
    try:
        user = state.get("user") or {}
        user_id = user.get("userId") or user.get("id") or None
        role_name = user.get("role", "Intern")
        question = state.get("question", "")
        agent_used = state.get("agent_chosen", "UNKNOWN")
        status = state.get("status", "Success")
        retrieved_docs = ", ".join(state.get("rag_docs") or []) if state.get("rag_docs") else "None"
        sql_executed = state.get("sql_query", "") or "None"

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO audit_logs 
                (user_id, role_name, question, agent_used, status, retrieved_documents, sql_executed)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, role_name, question, agent_used, status, retrieved_docs, sql_executed)
            )
            conn.commit()
    except Exception as e:
        print(f"[Audit Log Error] Failed to write audit log: {e}")
    finally:
        if conn and conn.open:
            conn.close()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set.")
    return ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=api_key, temperature=0.1)

# ==========================================
# 1. ROUTER NODE (Step 2 — LangGraph Router)
# ==========================================
def router_node(state: AgentState) -> AgentState:
    question = state["question"]
    lower_q = question.lower()

    # Step 1: Input Guardrails check
    blocked_keywords = ["ignore", "override", "bypass", "jailbreak", "confidential"]
    if any(word in lower_q for word in blocked_keywords):
        state["agent_chosen"] = "BLOCKED"
        state["status"] = "Blocked"
        state["answer"] = "Blocked: Input violates security guardrails."
        return state

    # Check conversation history for context (Step 6 - Memory)
    history_context = ""
    if state.get("history"):
        last_msgs = state["history"][-4:]
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in last_msgs])
        history_context = f"\nRecent Conversation History:\n{history_text}\n"

    # Ensure core company questions (About Nexora Systems, Founders & Leadership, Company History & Timeline)
    # always use HYBRID agent so all users (Intern, Employee, HR, Manager, CEO) get complete details from both RAG & MySQL!
    core_hybrid_keywords = [
        "about nexora", "nexora systems", "company profile", "who is nexora",
        "founders", "leadership", "who are the founders", "founder", "ceo name",
        "company history", "history", "timeline", "milestone"
    ]
    if any(kw in lower_q for kw in core_hybrid_keywords):
        state["agent_chosen"] = "HYBRID"
        state["status"] = "Allowed"
        return state

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an AI router for an enterprise knowledge assistant. "
         "You must choose the best data source for answering the user's question.\n"
         "Options:\n"
         "- RAG : Unstructured documents (policies, employee handbook, leave policy details, company history, general project descriptions).\n"
         "- SQL : Structured database tables (employee counts, salary bands, numeric revenue metrics, leadership list, department counts).\n"
         "- HYBRID : Queries requiring both document text and numeric database metrics (e.g. 'Summarize Project Falcon and tell me its contract value').\n\n"
         "Output EXACTLY one word: RAG, SQL, or HYBRID.{history_context}"),
        ("human", "{question}")
    ])
    res = (prompt | llm).invoke({"question": question, "history_context": history_context})
    chosen = res.content.strip().upper()

    if "HYBRID" in chosen:
        state["agent_chosen"] = "HYBRID"
    elif "SQL" in chosen:
        state["agent_chosen"] = "SQL"
    else:
        state["agent_chosen"] = "RAG"

    state["status"] = "Allowed"
    return state

# ==========================================
# 2. RAG NODE (Step 3 - RAG Agent)
# ==========================================
def run_rag(question: str, user: Optional[dict]) -> dict:
    vector_store = get_vector_store()
    search_kwargs = {"k": 6}
    # All users (Intern, Employee, HR, Manager, CEO) are authorized to view
    # About Nexora Systems, Founders & Leadership, Company History & Timeline, and policies.
    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
    docs = retriever.invoke(question)
    context = "\n\n".join([d.page_content for d in docs])
    doc_names = list(set([d.metadata.get("source", "Unknown Document") for d in docs]))
    return {"context": context, "doc_names": doc_names}

def rag_node(state: AgentState) -> AgentState:
    res = run_rag(state["question"], state.get("user"))
    state["rag_context"] = res["context"]
    state["rag_docs"] = res["doc_names"]
    return state

# ==========================================
# 3. SQL NODE (Step 3 - SQL Agent)
# ==========================================
def sql_node(state: AgentState) -> AgentState:
    res = query_mysql(state["question"], state.get("user"))
    state["sql_query"] = res.get("sql", "")
    if res.get("success"):
        state["sql_result"] = res.get("data")
    else:
        state["sql_result"] = None
        if "Access Denied" in res.get("error", ""):
            state["status"] = "Denied"
            state["answer"] = res.get("error")
    return state

# ==========================================
# 4. HYBRID NODE (Step 3 - Hybrid Agent)
# ==========================================
def hybrid_node(state: AgentState) -> AgentState:
    # Execute RAG
    rag_res = run_rag(state["question"], state.get("user"))
    state["rag_context"] = rag_res["context"]
    state["rag_docs"] = rag_res["doc_names"]

    # Execute SQL
    sql_res = query_mysql(state["question"], state.get("user"))
    state["sql_query"] = sql_res.get("sql", "")
    if sql_res.get("success"):
        state["sql_result"] = sql_res.get("data")
    else:
        state["sql_result"] = None
        if "Access Denied" in sql_res.get("error", ""):
            state["status"] = "Denied"
            state["answer"] = sql_res.get("error")
    return state

# ==========================================
# 5. GENERATE ANSWER NODE (Step 4 - Gemini LLM)
# ==========================================
def generate_answer_node(state: AgentState) -> AgentState:
    if state.get("status") in ["Denied", "Blocked"] and state.get("answer"):
        return state

    question = state["question"]
    rag_ctx = state.get("rag_context", "")
    sql_res = state.get("sql_result")
    history = state.get("history") or []

    # Format history
    history_text = ""
    if history:
        history_text = "\nConversation History:\n" + "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])

    # Check if data is empty (Step 5 - Retry Logic)
    has_rag = bool(rag_ctx and rag_ctx.strip())
    has_sql = bool(sql_res and len(str(sql_res)) > 2)

    if not has_rag and not has_sql:
        # If retries == 0, try fallback agent
        if state.get("retries", 0) == 0:
            state["retries"] = 1
            if state["agent_chosen"] == "RAG":
                state["agent_chosen"] = "SQL"
                state["status"] = "Fallback"
                state = sql_node(state)
                return generate_answer_node(state)
            elif state["agent_chosen"] == "SQL":
                state["agent_chosen"] = "RAG"
                state["status"] = "Fallback"
                state = rag_node(state)
                return generate_answer_node(state)

        state["answer"] = "Information not found."
        return state

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an AI assistant for Nexora Systems. "
         "Answer the user's question concisely and accurately based on the provided data.\n"
         "Rules:\n"
         "1. If the context and SQL results do not contain the answer, reply exactly: 'Information not found.'\n"
         "2. Keep answers professional and within 3-4 sentences unless a list is requested.\n"
         "3. Never hallucinate or invent numbers or policies.\n\n"
         "Document Context:\n{rag_context}\n\n"
         "Database SQL Results:\n{sql_result}{history_text}"),
        ("human", "{question}")
    ])

    res = (prompt | llm).invoke({
        "question": question,
        "rag_context": rag_ctx or "None",
        "sql_result": str(sql_res) if sql_res else "None",
        "history_text": history_text
    })

    answer = res.content.strip()
    if not answer or "i don't know" in answer.lower():
        answer = "Information not found."

    state["answer"] = answer
    state["status"] = "Success"
    return state

# ==========================================
# 6. AUDIT LOG NODE (Step 7 - Audit Log)
# ==========================================
def audit_node(state: AgentState) -> AgentState:
    log_audit_entry(state)
    return state

# ==========================================
# BUILD LANGGRAPH WORKFLOW
# ==========================================
def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("sql", sql_node)
    workflow.add_node("hybrid", hybrid_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("audit", audit_node)

    workflow.add_edge(START, "router")

    def route_decision(state: AgentState) -> str:
        if state.get("agent_chosen") == "BLOCKED":
            return "audit"
        elif state.get("agent_chosen") == "RAG":
            return "rag"
        elif state.get("agent_chosen") == "SQL":
            return "sql"
        elif state.get("agent_chosen") == "HYBRID":
            return "hybrid"
        return "rag"

    workflow.add_conditional_edges("router", route_decision, {
        "rag": "rag",
        "sql": "sql",
        "hybrid": "hybrid",
        "audit": "audit"
    })

    workflow.add_edge("rag", "generate_answer")
    workflow.add_edge("sql", "generate_answer")
    workflow.add_edge("hybrid", "generate_answer")
    workflow.add_edge("generate_answer", "audit")
    workflow.add_edge("audit", END)

    return workflow.compile()

# Global compiled graph
agent_graph = build_agent_graph()

def run_agentic_rag(question: str, user: dict = None, history: list = None) -> dict:
    """
    Main entry point for Step 5 Agentic AI:
    Executes the compiled LangGraph workflow and returns answer, agent chosen, and metadata.
    """
    initial_state: AgentState = {
        "question": question,
        "user": user or {},
        "history": history or [],
        "agent_chosen": "",
        "rag_context": "",
        "rag_docs": [],
        "sql_result": None,
        "sql_query": "",
        "answer": "",
        "status": "Starting",
        "retries": 0
    }
    final_state = agent_graph.invoke(initial_state)
    return {
        "answer": final_state.get("answer", "Information not found."),
        "agent_chosen": final_state.get("agent_chosen", "RAG"),
        "sql_query": final_state.get("sql_query", ""),
        "rag_docs": final_state.get("rag_docs", []),
        "status": final_state.get("status", "Success")
    }
