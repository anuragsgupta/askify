import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Mail, FileSpreadsheet, CheckCircle2, ChevronDown, ChevronUp, Loader, Plus, MessageSquare, Trash2 } from 'lucide-react';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);
  const messagesEndRef = useRef(null);
  const [expandedSource, setExpandedSource] = useState(null);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showSessions, setShowSessions] = useState(false);

  // Store last response globally for CRM ticket
  useEffect(() => {
    if (lastResponse) {
      window.__lastRagResponse = lastResponse;
    }
  }, [lastResponse]);

  // Load recent sessions on mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const res = await fetch('/api/sessions?limit=20');
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const createNewSession = async () => {
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'New Chat' })
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentSessionId(data.session_id);
        setMessages([]);
        setLastResponse(null);
        await loadSessions();
      }
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const res = await fetch(`/api/sessions/${sessionId}`);
      if (res.ok) {
        const data = await res.json();
        const historyMessages = [];
        data.history.forEach(item => {
          historyMessages.push({ sender: 'user', text: item.question });
          historyMessages.push({ sender: 'ai', text: item.answer });
        });
        setMessages(historyMessages);
        setCurrentSessionId(sessionId);
        
        // Set last response to restore right sidebar
        if (data.history.length > 0) {
          const latest = data.history[data.history.length - 1];
          setLastResponse({
            answer: latest.answer,
            sources: latest.sources || [],
            conflict_analysis: latest.conflict_analysis || null
          });
        }
        setShowSessions(false);
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation();
    if (!confirm('Delete this chat session?')) return;
    
    try {
      const res = await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
      if (res.ok) {
        if (currentSessionId === sessionId) {
          setCurrentSessionId(null);
          setMessages([]);
          setLastResponse(null);
        }
        await loadSessions();
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const question = inputValue.trim();
    setMessages(prev => [...prev, { sender: 'user', text: question }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question, 
          n_results: 10,
          session_id: currentSessionId 
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Query failed');
      }

      const data = await res.json();
      setLastResponse(data);
      setMessages(prev => [...prev, { sender: 'ai', text: data.answer }]);
      
      // Update current session ID if it was created
      if (data.session_id && !currentSessionId) {
        setCurrentSessionId(data.session_id);
        await loadSessions();
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'ai', text: `❌ Error: ${err.message}` }]);
      setLastResponse(null);
    }

    setIsLoading(false);
  };

  const getSourceIcon = (type) => {
    if (type === 'pdf') return FileText;
    if (type === 'excel' || type === 'xlsx' || type === 'xls') return FileSpreadsheet;
    return Mail;
  };

  const getSourceColor = (type) => {
    if (type === 'pdf') return '#f59e0b';
    if (type === 'excel' || type === 'xlsx' || type === 'xls') return '#10b981';
    return '#3b82f6';
  };

  const formatConflictValues = (valueString) => {
    // Split by comma and wrap each value in a span
    if (!valueString) return null;
    const values = valueString.split(',').map(v => v.trim()).filter(v => v);
    return values.map((val, idx) => (
      <span key={idx} className="conflict-val-item">{val}</span>
    ));
  };

  const conflict = lastResponse?.conflict_analysis || null;
  const sources = lastResponse?.sources || [];

  return (
    <div className="chat-page animate-fade-in">
      {/* Left Column: Chat Window */}
      <div className="chat-left glass-panel">
        <div className="chat-header">
          <h3>Chat</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              className="icon-btn" 
              onClick={() => setShowSessions(!showSessions)}
              title="Recent Sessions"
              style={{ backgroundColor: showSessions ? 'var(--primary-color)' : 'transparent', color: showSessions ? 'white' : 'var(--text-color)' }}
            >
              <MessageSquare size={18} />
            </button>
            <button 
              className="icon-btn" 
              onClick={createNewSession}
              title="New Chat Session"
            >
              <Plus size={18} />
            </button>
          </div>
        </div>
        
        {/* Recent Sessions Dropdown */}
        {showSessions && (
          <div className="sessions-dropdown glass-panel" style={{ 
            position: 'absolute', 
            top: '60px', 
            left: '16px', 
            right: '16px', 
            maxHeight: '300px', 
            overflowY: 'auto',
            zIndex: 10,
            padding: '12px'
          }}>
            <h4 style={{ margin: '0 0 12px 0', fontSize: '0.9rem', color: 'var(--text-muted)' }}>Recent Sessions</h4>
            {sessions.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No sessions yet</p>
            ) : (
              sessions.map(session => (
                <div 
                  key={session.id} 
                  className="session-item"
                  onClick={() => loadSession(session.id)}
                  style={{
                    padding: '10px 12px',
                    marginBottom: '8px',
                    backgroundColor: currentSessionId === session.id ? 'var(--primary-color)15' : 'var(--bg-secondary)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--primary-color)20'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = currentSessionId === session.id ? 'var(--primary-color)15' : 'var(--bg-secondary)'}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 500, marginBottom: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {session.title}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {session.message_count} messages • {new Date(session.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button
                    className="icon-btn"
                    onClick={(e) => deleteSession(session.id, e)}
                    style={{ padding: '6px', marginLeft: '8px' }}
                    title="Delete session"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        )}
        
        <div className="chat-messages premium-scroll">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 20px' }}>
              <p style={{ fontSize: '1.1rem', marginBottom: '8px' }}>Ask a question about your documents</p>
              <p style={{ fontSize: '0.85rem' }}>e.g. "What is our refund policy for bulk orders?"</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble-container ${msg.sender}`}>
              <div className={`chat-bubble ${msg.sender}`}>
                {msg.text}
                
                {/* Show inline conflict warning for AI messages */}
                {msg.sender === 'ai' && lastResponse && lastResponse.conflict_analysis?.has_conflicts && i === messages.length - 1 && (
                  <div className="conflict-warning">
                    <div className="conflict-warning-title">
                      ⚠️ Conflict Detected: Multiple Sources with Different Information
                    </div>
                    <div className="conflict-warning-content">
                      {lastResponse.conflict_analysis.conflicts[0]?.sources?.map((src, idx) => (
                        <div key={idx} className="conflict-source-inline">
                          <span className="conflict-source-label">Source {idx + 1}:</span>
                          <span>{src.source}</span>
                          <span style={{ color: '#dc2626', fontWeight: 600 }}>({src.value})</span>
                          <span style={{ color: '#78350f' }}>{src.date || 'No date'}</span>
                        </div>
                      ))}
                    </div>
                    <div className="conflict-resolution-inline">
                      <strong>Resolution:</strong> {lastResponse.conflict_analysis.conflicts[0]?.resolution?.reason}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble-container ai">
              <div className="chat-bubble ai" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Loader size={16} style={{ animation: 'spin 1s linear infinite' }} />
                Analyzing knowledge base...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="chat-input-area">
          <form onSubmit={handleSend} className="chat-input-box">
            <input
              type="text"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <button type="submit" className="send-btn" disabled={isLoading}><Send size={18} /></button>
          </form>
        </div>
      </div>

      {/* Right Column Grid */}
      <div className="chat-right">

        {/* Conflict Analysis */}
        <div className="chat-conflict glass-panel">
          <h3>Conflict Analysis</h3>
          {conflict && conflict.has_conflicts ? (
            <>
              <div className="conflict-table-header">
                <span>Source</span>
                <span>Value</span>
                <span>Date</span>
              </div>
              <div className="conflict-rows">
                {conflict.conflicts[0]?.sources?.map((src, i) => {
                  const Icon = getSourceIcon(src.source_type);
                  const color = getSourceColor(src.source_type);
                  return (
                    <div key={i} className="conflict-row">
                      <div className="conflict-source">
                        <div className="source-icon" style={{ backgroundColor: `${color}15`, color }}>
                          <Icon size={16} />
                        </div>
                        <span>{src.source}</span>
                      </div>
                      <div className="conflict-val">
                        {formatConflictValues(src.value)}
                      </div>
                      <div className="conflict-date">{src.date || '—'}</div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {sources.length > 0 ? 'No conflicts detected across sources.' : 'Ask a question to see analysis.'}
            </p>
          )}
        </div>

        {/* Final Decision */}
        <div className="chat-decision glass-panel">
          <h3>Final Decision</h3>
          {conflict && conflict.has_conflicts ? (
            <>
              <div className="decision-banner">
                <CheckCircle2 color="var(--success-color)" size={20} />
                <span>Trusted: {conflict.conflicts[0]?.resolution?.chosen_source}</span>
              </div>
              <div className="decision-detail">
                <h4>Detailed Reason</h4>
                <p>{conflict.conflicts[0]?.resolution?.reason}</p>
              </div>
              <div className="decision-confidence">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span>Confidence</span>
                  <strong>{Math.round((conflict.conflicts[0]?.resolution?.confidence || 0) * 100)}%</strong>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${(conflict.conflicts[0]?.resolution?.confidence || 0) * 100}%`, backgroundColor: 'var(--success-color)' }}></div>
                </div>
              </div>
            </>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              {sources.length > 0 ? 'All sources agree — no resolution needed.' : 'Waiting for query results.'}
            </p>
          )}
        </div>

        {/* Source Details Accordions */}
        <div className="chat-sources glass-panel">
          <h3>Source Details</h3>
          <div className="sources-list premium-scroll">
            {sources.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No sources to display yet.</p>
            ) : (
              sources.map((src, i) => {
                const color = getSourceColor(src.source_type);
                const isExpanded = expandedSource === i;
                return (
                  <div key={i} className="source-accordion" onClick={() => setExpandedSource(isExpanded ? null : i)}>
                    <div className="source-accordion-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}>
                        <span style={{ backgroundColor: `${color}15`, color, padding: '4px 12px', borderRadius: '16px', fontSize: '0.85rem' }}>{src.source_type?.toUpperCase()}</span>
                        <span style={{ fontSize: '0.9rem' }}>{src.source}</span>
                      </div>
                      {isExpanded ? <ChevronUp size={18} color="var(--text-muted)" /> : <ChevronDown size={18} color="var(--text-muted)" />}
                    </div>
                    {isExpanded && (
                      <div style={{ marginTop: '12px', padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px', fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                        <p><strong>Location:</strong> {src.location}</p>
                        <p><strong>Relevance:</strong> {Math.round(src.relevance_score * 100)}%</p>
                        <p style={{ marginTop: '8px' }}>{src.text_excerpt}</p>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Chat;
