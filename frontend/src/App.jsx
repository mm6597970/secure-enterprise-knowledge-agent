import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Users, Bot, Send, Upload } from 'lucide-react';
import './index.css';

const API_BASE_URL = 'http://localhost:5000';

const MYSQL_ENDPOINTS = [
  { name: 'Health', path: '/health' },
  { name: 'Employees', path: '/employees' },
  { name: 'Emp(1)', path: '/employees/1' },
  { name: 'Leave Policy', path: '/leave-policy' },
  { name: 'Company', path: '/company' },
  { name: 'Leadership', path: '/leadership' },
  { name: 'History', path: '/history' },
  { name: 'Income', path: '/income' },
  { name: 'Collabs', path: '/collaborations' },
  { name: 'Cur Projects', path: '/projects/current' },
  { name: 'Past Projects', path: '/projects/past' }
];

function App() {
  const [activeTab, setActiveTab] = useState(MYSQL_ENDPOINTS[0]);
  const [mysqlData, setMysqlData] = useState(null);
  const [loadingMysql, setLoadingMysql] = useState(false);

  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! Ask me a question about the company or upload a document to the knowledge base.' }
  ]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const messagesEndRef = useRef(null);

  // Fetch MySQL Data whenever the active tab changes
  useEffect(() => {
    setLoadingMysql(true);
    axios.get(`${API_BASE_URL}${activeTab.path}`)
      .then(res => setMysqlData(res.data))
      .catch(err => {
        console.error(`Error fetching ${activeTab.path}:`, err);
        setMysqlData({ error: 'Failed to fetch data. Is the backend running?' });
      })
      .finally(() => setLoadingMysql(false));
  }, [activeTab]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, { question: userMessage });
      setMessages(prev => [...prev, { role: 'ai', content: response.data.answer || 'No answer received.' }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { role: 'ai', content: 'Error communicating with AI service.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setMessages(prev => [...prev, { role: 'user', content: `Uploading document: ${file.name}...` }]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessages(prev => [...prev, { role: 'ai', content: `Success! ${file.name} has been processed and added to the RAG knowledge base.` }]);
    } catch (error) {
      console.error("Upload error:", error);
      setMessages(prev => [...prev, { role: 'ai', content: `Failed to upload ${file.name}.` }]);
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Secure Enterprise Dashboard</h1>
        <p>Unified Interface for MySQL Data and AI Knowledge Retrieval</p>
      </header>

      {/* Left Column: MySQL Data */}
      <div className="card">
        <h2><Users size={24} color="#818cf8" /> Database Explorer (MySQL)</h2>
        
        <div className="tabs">
          {MYSQL_ENDPOINTS.map(endpoint => (
            <button 
              key={endpoint.name}
              className={`tab ${activeTab.name === endpoint.name ? 'active' : ''}`}
              onClick={() => setActiveTab(endpoint)}
            >
              {endpoint.name}
            </button>
          ))}
        </div>

        <div className="employee-list">
          {loadingMysql ? (
            <p style={{ color: 'var(--text-muted)' }}>Loading {activeTab.name}...</p>
          ) : activeTab.name === 'Employees' && Array.isArray(mysqlData) ? (
            mysqlData.map(emp => (
              <div key={emp.ID || Math.random()} className="employee-card">
                <h3>{emp.Employee}</h3>
                <p>{emp.Role} - {emp.Department}</p>
                <small>Manager: {emp.Manager || 'None'} | Salary: {emp.Salary} LPA</small>
              </div>
            ))
          ) : (
             <div className="data-view">
               {JSON.stringify(mysqlData, null, 2)}
             </div>
          )}
        </div>
      </div>

      {/* Right Column: FastAPI RAG AI */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '1rem', marginBottom: '1rem' }}>
           <h2 style={{ borderBottom: 'none', padding: 0, margin: 0 }}><Bot size={24} color="#c084fc" /> AI Assistant (RAG)</h2>
           
           <label className="upload-btn" style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.1)', padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.9rem' }}>
             <Upload size={16} />
             {uploading ? 'Uploading...' : 'Upload Doc'}
             <input type="file" style={{ display: 'none' }} accept=".pdf,.txt,.docx" onChange={handleFileUpload} disabled={uploading} />
           </label>
        </div>

        <div className="chat-box">
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {loading && (
              <div className="message ai">
                <span className="loader" style={{ display: 'inline-block', width: '12px', height: '12px', marginRight: '8px' }}></span> Thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="input-group">
            <input 
              type="text" 
              placeholder="e.g., What is the casual leave policy?"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading || !chatInput.trim()}>
              <Send size={18} />
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
