import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { BarChart2 } from 'lucide-react';
import './TopBar.css';

const TopBar = () => {
  const location = useLocation();
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const getPageTitle = () => {
    const path = location.pathname.substring(1);
    if (!path) return 'Dashboard';
    return path.charAt(0).toUpperCase() + path.slice(1);
  };

  return (
    <>
      <header className="topbar">
        <h1 className="page-title">{getPageTitle()}</h1>
        <div className="topbar-actions">
          <button className="btn-secondary">
            <BarChart2 size={18} />
            Analytics
          </button>
          <button className="btn-primary" onClick={() => setIsModalOpen(true)}>
            Create Support Ticket
          </button>
        </div>
      </header>

      {/* Mock CRM Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content glass-panel animate-fade-in" onClick={e => e.stopPropagation()}>
            <h2 style={{ marginBottom: '16px' }}>Create Support Ticket</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
              Auto-populated from active RAG context.
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
               <div>
                 <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '0.875rem' }}>Subject</label>
                 <input type="text" defaultValue="Refund Policy Inquiry" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', outline: 'none' }} />
               </div>
               <div>
                 <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '0.875rem' }}>Description</label>
                 <textarea rows="4" defaultValue="Based on recent AI response: User is inquiring about 100% refund policy for bulk orders..." style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', outline: 'none', resize: 'none' }}></textarea>
               </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
              <button className="btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
              <button className="btn-primary" onClick={() => { alert('Ticket Created!'); setIsModalOpen(false); }}>Submit Ticket</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TopBar;
