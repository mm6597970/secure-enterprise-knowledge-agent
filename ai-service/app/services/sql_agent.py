import os
import re
import pymysql
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "student001")
DB_NAME = os.getenv("DB_NAME", "nexora_systems")

MYSQL_SCHEMA_DESCRIPTION = """
Database: nexora_systems
Tables:
1. company_info(id, legal_name, founded_year, headquarters, secondary_office, industry, ceo_name, cofounder_name, employee_strength, company_type)
2. leadership(leader_id, name, designation, joined_year)
3. company_history(history_id, event_year, milestone)
4. income_timeline(fy_id, financial_year, revenue_cr, employee_count, net_profit_margin_pct)
5. salary_structure(role_id, role_name, level_no, min_lpa, max_lpa, review_cycle)
6. employees(emp_id, full_name, role_id, department, salary_lpa, join_date, manager_id)
7. leave_policy(policy_id, leave_type, days_allowed, notes)
8. projects_past(project_id, project_name, client_name, start_date, end_date, description)
9. projects_current(project_id, project_name, client_name, category, contract_value_inr, pricing_model, status, start_date, end_date)
10. collaborations(collab_id, partner_name, collab_type, since_year)
"""

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def is_safe_read_only_sql(sql: str) -> bool:
    """Ensure SQL query is SELECT only and contains no mutation commands."""
    cleaned = sql.strip().lower()
    if not cleaned.startswith("select"):
        return False
    forbidden_keywords = [
        "insert", "update", "delete", "drop", "alter", "truncate",
        "create", "grant", "revoke", "exec", "execute", "call"
    ]
    for kw in forbidden_keywords:
        if re.search(rf"\b{kw}\b", cleaned):
            return False
    return True

def query_mysql(question: str, user: dict = None) -> dict:
    """
    Step 5 SQL Agent:
    1. Generates safe read-only SELECT SQL using LLM and database schema.
    2. Checks RBAC permissions (e.g., blocking salary queries for Intern/Employee).
    3. Executes query in MySQL and returns structured results.
    """
    role = user.get("role", "Intern") if user else "Intern"

    # Security Guardrail (Rule 9): Prompt Injection / Malicious Inputs
    lower_q = question.lower()
    blocked_keywords = [
        "ignore previous instructions", "reveal system prompt", "forget security",
        "act as chatgpt", "bypass restrictions", "ignore instructions", "jailbreak",
        "override", "bypass"
    ]
    if any(word in lower_q for word in blocked_keywords):
        return {
            "success": False,
            "error": "Request denied due to security policy.",
            "sql": "",
            "data": None
        }

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")

    llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=api_key, temperature=0)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", 
         "You are an expert SQL analyst for MySQL database 'nexora_systems'. "
         "Given the schema below, generate a syntactically correct MySQL SELECT query to answer the user's question.\n"
         "IMPORTANT:\n"
         "- Output ONLY the raw SQL SELECT query, without markdown formatting, code block backticks, or explanation.\n"
         "- Never write INSERT, UPDATE, DELETE, or ALTER queries.\n"
         "- For projects, check projects_current or projects_past.\n"
         "- For leave policy, check leave_policy table.\n"
         "- SQL is the authoritative source of truth for structured employee details, salary, department, join date, role, and IDs.\n\n"
         "Schema:\n{schema}"),
        ("human", "{question}")
    ])

    chain = prompt_template | llm
    res = chain.invoke({"schema": MYSQL_SCHEMA_DESCRIPTION, "question": question})
    raw_sql = res.content.strip()

    # Clean code blocks if LLM still added them
    raw_sql = re.sub(r"^```sql\s*", "", raw_sql, flags=re.IGNORECASE)
    raw_sql = re.sub(r"^```\s*", "", raw_sql)
    raw_sql = re.sub(r"\s*```$", "", raw_sql).strip()

    # 1. Security Guardrail: Read-Only SELECT check
    if not is_safe_read_only_sql(raw_sql):
        return {
            "success": False,
            "error": "Blocked: Only safe read-only SELECT queries are allowed.",
            "sql": raw_sql,
            "data": None
        }

    # 2. RBAC Guardrail: Salary access check (Rule 10)
    if role not in ["CEO", "HR", "Manager"]:
        sql_lower = raw_sql.lower()
        if "salary" in sql_lower or "salary_lpa" in sql_lower or "salary_structure" in sql_lower:
            return {
                "success": False,
                "error": "Access denied. You do not have permission to access this information.",
                "sql": raw_sql,
                "data": None
            }

    # 3. Execute in MySQL
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(raw_sql)
            rows = cursor.fetchall()
        return {
            "success": True,
            "sql": raw_sql,
            "data": rows
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql": raw_sql,
            "data": None
        }
    finally:
        if conn and conn.open:
            conn.close()
