import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import './TopBar.css';

const TopBar = () => {
  const location = useLocation();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [ticketSubject, setTicketSubject] = useState('');
  const [ticketDesc, setTicketDesc] = useState('');
  
  const getPageTitle = () => {
    const path = location.pathname.substring(1);
    if (!path) return 'Dashboard';
    return path.charAt(0).toUpperCase() + path.slice(1);
  };

  const openTicketModal = () => {
    // Pull context from last RAG response if available
    const lastResponse = window.__lastRagResponse;
    if (lastResponse) {
      const sources = (lastResponse.sources || []).map(s => s.source).join(', ');
      setTicketSubject(`Query: ${lastResponse.answer?.substring(0, 60)}...`);
      setTicketDesc(
        `AI Response Summary:\n${lastResponse.answer?.substring(0, 300)}\n\n` +
        `Sources referenced: ${sources}\n\n` +
        (lastResponse.conflict_analysis?.has_conflicts
          ? `⚠️ Conflicts detected: ${lastResponse.conflict_analysis.conflicts[0]?.resolution?.reason || 'See details.'}`
          : 'No conflicts detected across sources.')
      );
    } else {
      setTicketSubject('');
      setTicketDesc('');
    }
    setIsModalOpen(true);
  };

  return (
    <>
      <header className="topbar">
        <h1 className="page-title">{getPageTitle()}</h1>
        <div className="topbar-actions">
          <button className="btn-primary" onClick={openTicketModal}>
            Create Support Ticket
          </button>
        </div>
      </header>

      {/* CRM Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content glass-panel animate-fade-in" onClick={e => e.stopPropagation()}>
            <h2 style={{ marginBottom: '16px' }}>Create Support Ticket</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
              {ticketSubject ? 'Auto-populated from your last RAG query.' : 'No active RAG context — fill in manually.'}
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
               <div>
                 <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '0.875rem' }}>Subject</label>
                 <input
                   type="text"
                   value={ticketSubject}
                   onChange={(e) => setTicketSubject(e.target.value)}
                   placeholder="Ticket subject..."
                   style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', outline: 'none' }}
                 />
               </div>
               <div>
                 <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '0.875rem' }}>Description</label>
                 <textarea
                   rows="6"
                   value={ticketDesc}
                   onChange={(e) => setTicketDesc(e.target.value)}
                   placeholder="Ticket description..."
                   style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', outline: 'none', resize: 'none', fontFamily: 'inherit' }}
                 />
               </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
              <button className="btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
              <button className="btn-primary" onClick={() => { alert('✅ Support Ticket Created Successfully!'); setIsModalOpen(false); }}>Submit Ticket</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TopBar;
