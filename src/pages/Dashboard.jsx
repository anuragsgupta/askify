import React from 'react';
import { Database, FileText, Search, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const cards = [
    { title: 'Total Documents indexed', value: '1,248', icon: Database, color: '#3b82f6' },
    { title: 'Active RAG Queries', value: '84', icon: Search, color: '#10b981' },
    { title: 'Data Conflicts Detected', value: '12', icon: AlertCircle, color: '#f59e0b' },
    { title: 'Supported Formats', value: 'PDF, Excel, EML', icon: FileText, color: '#8b5cf6' },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        {cards.map((card, i) => (
          <div key={i} className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '8px', fontWeight: 500 }}>{card.title}</p>
              <h3 style={{ fontSize: '1.75rem', fontWeight: 700 }}>{card.value}</h3>
            </div>
            <div style={{ padding: '12px', background: `${card.color}15`, borderRadius: '12px', color: card.color }}>
              <card.icon size={24} />
            </div>
          </div>
        ))}
      </div>

      <div className="glass-panel" style={{ padding: '24px', flex: 1, minHeight: '300px' }}>
        <h3 style={{ marginBottom: '16px', fontWeight: 600 }}>System Status</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          The multi-format Retrieval-Augmented Generation pipeline is running normally. 
          Vector database synchronization is complete.
        </p>
        <div style={{ marginTop: '30px' }}>
             <p style={{marginBottom: '10px'}}>Semantic Search Integrity:</p>
             <div style={{ width: '100%', backgroundColor: 'var(--border-color)', height: '8px', borderRadius: '4px' }}>
                 <div style={{ width: '98%', backgroundColor: 'var(--success-color)', height: '100%', borderRadius: '4px' }}></div>
             </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
