import React, { useState } from 'react';
import { Send, FileText, Mail, FileSpreadsheet, CheckCircle2, ChevronDown } from 'lucide-react';
import './Chat.css';

const MOCK_MESSAGES = [
  { sender: 'user', text: 'What is our refund policy for bulk orders quoted to Acme Corp last month?' },
  { sender: 'ai', text: 'Based on the provided documents, I have analyzed the conflicting information regarding the refund policy for Acme Corp.\n\nThe Email from Feb 20 suggests a 50% refund, while the older policy PDF states 70%. However, the most recent Excel Record from Mar 12, which overrides earlier correspondence, confirms a 100% refund was approved for this specific bulk order.' }
];

const SOURCES = [
  { type: 'email', name: 'Email', value: '50%', date: 'Feb 20', color: '#3b82f6', icon: Mail, confidence: 40 },
  { type: 'pdf', name: 'PDF Policy', value: '70%', date: 'Mar 1', color: '#f59e0b', icon: FileText, confidence: 60 },
  { type: 'excel', name: 'Excel Record', value: '100%', date: 'Mar 12', color: '#10b981', icon: FileSpreadsheet, confidence: 95 }
];

const Chat = () => {
  const [messages, setMessages] = useState(MOCK_MESSAGES);
  const [inputValue, setInputValue] = useState('');

  const handleSend = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    setMessages([...messages, { sender: 'user', text: inputValue }]);
    setInputValue('');
    
    // Mock simple AI loading response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: 'Thank you for your question. Based on the indexed data, I recommend creating a support ticket so I can evaluate the exact records.' 
      }]);
    }, 1500);
  };

  return (
    <div className="chat-page animate-fade-in">
      {/* Left Column: Chat Window */}
      <div className="chat-left glass-panel">
        <div className="chat-header">
          <h3>Chat</h3>
        </div>
        <div className="chat-messages premium-scroll">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble-container ${msg.sender}`}>
              <div className={`chat-bubble ${msg.sender}`}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>
        <div className="chat-input-area">
          <form onSubmit={handleSend} className="chat-input-box">
            <input 
              type="text" 
              placeholder="Type your message..." 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <button type="submit" className="send-btn"><Send size={18} /></button>
          </form>
        </div>
      </div>

      {/* Right Column Grid */}
      <div className="chat-right">
        
        {/* Conflict Analysis */}
        <div className="chat-conflict glass-panel">
          <h3>Conflict Analysis</h3>
          <div className="conflict-table-header">
            <span>Source</span>
            <span>Value</span>
            <span>Date</span>
          </div>
          <div className="conflict-rows">
            {SOURCES.map((src, i) => (
              <div key={i} className="conflict-row">
                <div className="conflict-source">
                  <div className="source-icon" style={{ backgroundColor: `${src.color}15`, color: src.color }}>
                    <src.icon size={16} />
                  </div>
                  <span>{src.name}</span>
                </div>
                <div className="conflict-val" style={{ color: '#ef4444', backgroundColor: 'var(--error-bg)' }}>{src.value}</div>
                <div className="conflict-date">{src.date}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Final Decision */}
        <div className="chat-decision glass-panel">
          <h3>Final Decision</h3>
          <div className="decision-banner">
            <CheckCircle2 color="var(--success-color)" size={20} />
            <span>100% Refund Approved</span>
          </div>
          
          <div className="decision-detail">
            <h4>Detailed Reason</h4>
            <p>100% Refund Approved based on the most recent Excel pricing confirmation. The system prioritized the tabular record (Mar 12) over the unstructured email history (Feb 20).</p>
          </div>

          <div className="decision-confidence">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span>Confidence</span>
              <strong>95%</strong>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: '95%', backgroundColor: 'var(--success-color)' }}></div>
            </div>
          </div>
        </div>

        {/* Source Details Accordions */}
        <div className="chat-sources glass-panel">
          <h3>Source Details</h3>
          <div className="sources-list premium-scroll">
            {SOURCES.map((src, i) => (
              <div key={i} className="source-accordion">
                <div className="source-accordion-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: src.color, fontWeight: 500 }}>
                    <span style={{ backgroundColor: `${src.color}15`, padding: '4px 12px', borderRadius: '16px' }}>{src.name}</span>
                  </div>
                  <ChevronDown size={18} color="var(--text-muted)" />
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Chat;
