import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Users, Bot, Send, Upload, Lock, LogOut } from 'lucide-react';
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
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('user')) || null;
    } catch {
      return null;
    }
  });
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'night');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [loggingIn, setLoggingIn] = useState(false);

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

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);


  const handleLogin = async (e) => {
    e.preventDefault();
    setLoggingIn(true);
    setLoginError('');
    try {
      const res = await axios.post(`${API_BASE_URL}/auth/login`, { email, password });
      if (res.data.success) {
        setToken(res.data.token);
        setUser(res.data.user);
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('user', JSON.stringify(res.data.user));
      }
    } catch (err) {
      setLoginError(err.response?.data?.message || 'Login failed');
    } finally {
      setLoggingIn(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setMessages([{ role: 'ai', content: 'Hello! Ask me a question about the company or upload a document to the knowledge base.' }]);
  };

  const getAuthHeaders = () => ({
    headers: { Authorization: `Bearer ${token}` }
  });

  // Fetch MySQL Data whenever the active tab changes
  useEffect(() => {
    if (!token) return;
    setLoadingMysql(true);
    axios.get(`${API_BASE_URL}${activeTab.path}`, getAuthHeaders())
      .then(res => setMysqlData(res.data))
      .catch(err => {
        console.error(`Error fetching ${activeTab.path}:`, err);
        if (err.response?.status === 401) handleLogout();
        setMysqlData({ error: 'Failed to fetch data or unauthorized.' });
      })
      .finally(() => setLoadingMysql(false));
  }, [activeTab, token]);

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
      const response = await axios.post(`${API_BASE_URL}/chat`, { question: userMessage }, getAuthHeaders());
      setMessages(prev => [...prev, { role: 'ai', content: response.data.answer || 'No answer received.' }]);
    } catch (error) {
      console.error("Chat error:", error);
      if (error.response?.status === 401) handleLogout();
      setMessages(prev => [...prev, { role: 'ai', content: 'Error: ' + (error.response?.data?.message || 'Unauthorized or service unavailable.') }]);
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
        headers: { 'Content-Type': 'multipart/form-data', Authorization: `Bearer ${token}` }
      });
      setMessages(prev => [...prev, { role: 'ai', content: `Success! ${file.name} has been processed and added to the RAG knowledge base.` }]);
    } catch (error) {
      console.error("Upload error:", error);
      if (error.response?.status === 401) handleLogout();
      setMessages(prev => [...prev, { role: 'ai', content: `Failed to upload ${file.name}.` }]);
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  if (!token) {
    return (
      <div className="container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100vh' }}>
        
        <div style={{ alignSelf: 'flex-end', marginBottom: '2rem', display: 'flex', gap: '0.5rem' }}>
          <button onClick={() => setTheme('day')} style={{ padding: '0.5rem', fontSize: '0.8rem', background: theme === 'day' ? 'var(--primary)' : 'rgba(128,128,128,0.2)' }}>Day</button>
          <button onClick={() => setTheme('evening')} style={{ padding: '0.5rem', fontSize: '0.8rem', background: theme === 'evening' ? 'var(--primary)' : 'rgba(128,128,128,0.2)' }}>Evening</button>
          <button onClick={() => setTheme('night')} style={{ padding: '0.5rem', fontSize: '0.8rem', background: theme === 'night' ? 'var(--primary)' : 'rgba(128,128,128,0.2)' }}>Night</button>
        </div>

        <div className="card" style={{ maxWidth: '400px', width: '100%', margin: 'auto' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <Lock size={24} color="#818cf8" style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            Secure Login
          </h2>
          {loginError && <div style={{ color: '#ef4444', background: '#fee2e2', padding: '10px', borderRadius: '4px', marginBottom: '1rem', textAlign: 'center' }}>{loginError}</div>}
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input 
              type="email" 
              placeholder="Email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }}
            />
            <input 
              type="password" 
              placeholder="Password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              style={{ padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }}
            />
            <button type="submit" disabled={loggingIn} style={{ padding: '0.75rem', background: '#818cf8', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>
              {loggingIn ? 'Logging in...' : 'Login'}
            </button>
          </form>
          <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <strong>Demo Accounts:</strong><br/>
            arvind.rajan@nexorasystems.com (CEO)<br/>
            divya.iyer@nexorasystems.com (HR)<br/>
            anjali.ramesh@nexorasystems.com (Employee)<br/>
            deepa.narayan@nexorasystems.com (Intern)<br/>
            <em>Password: password</em>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginBottom: '-1rem' }}>
        <button onClick={() => setTheme('day')} style={{ padding: '0.5rem', fontSize: '0.8rem', background: theme === 'day' ? 'var(--primary)' : 'rgba(128,128,128,0.2)' }}>Day</button>
        <button onClick={() => setTheme('evening')} style={{ padding: '0.5rem', fontSize: '0.8rem', background: theme === 'evening' ? 'var(--primary)' : 'rgba(128,128,128,0.2)' }}>Evening</button>
        <button onClick={() => setTheme('night')} style={{ padding: '0.5rem', fontSize: '0.8rem', background: theme === 'night' ? 'var(--primary)' : 'rgba(128,128,128,0.2)' }}>Night</button>
      </div>

      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ textAlign: 'left' }}>
          <h1>Secure Enterprise Dashboard</h1>
          <p>Unified Interface for MySQL Data and AI Knowledge Retrieval</p>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
          {user && (
            <div style={{ background: 'var(--card-bg)', padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid var(--border)', textAlign: 'right' }}>
              <div style={{ fontWeight: 'bold', color: 'var(--text)' }}>{user.name}</div>
              <div style={{ fontSize: '0.85rem', color: '#818cf8' }}>{user.role}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{user.email}</div>
            </div>
          )}
          <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#ef4444', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '8px', cursor: 'pointer' }}>
            <LogOut size={16} /> Logout
          </button>
        </div>
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
              placeholder="Ask a question (e.g., Show CEO salary)"
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
