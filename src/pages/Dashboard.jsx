import React, { useState, useEffect } from 'react';
import { Database, FileText, Search, AlertCircle, Loader, Clock, FileSpreadsheet, Mail } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, historyRes, docsRes] = await Promise.all([
          fetch('/api/stats'),
          fetch('/api/history?limit=5'),
          fetch('/api/documents')
        ]);
        
        if (statsRes.ok) setStats(await statsRes.json());
        if (historyRes.ok) {
            const hData = await historyRes.json();
            setHistory(hData.history || []);
        }
        if (docsRes.ok) {
            const dData = await docsRes.json();
            const sortedDocs = (dData.documents || [])
                .filter(d => d.upload_date)
                .sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date))
                .slice(0, 5);
            setDocuments(sortedDocs);
        }
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  const cards = [
    { title: 'Documents Indexed', value: stats?.total_documents ?? '—', icon: Database, color: '#3b82f6' },
    { title: 'Total Chunks', value: stats?.total_chunks ?? '—', icon: Search, color: '#10b981' },
    { title: 'Supported Formats', value: stats?.supported_formats ?? 'PDF, Excel, TXT', icon: FileText, color: '#8b5cf6' },
    { title: 'System Status', value: stats ? 'Online' : 'Offline', icon: AlertCircle, color: stats ? '#10b981' : '#ef4444' },
  ];

  const formatTimeAgo = (dateStr) => {
    if (!dateStr) return 'unknown time';
    const diffHours = Math.round((new Date() - new Date(dateStr)) / (1000 * 60 * 60));
    if (diffHours < 1) return 'just now';
    if (diffHours === 1) return 'about 1 hour ago';
    if (diffHours < 24) return `about ${diffHours} hours ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `about ${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  const getSourceIcon = (type) => {
    if (type === 'pdf') return <FileText size={18} color="#ef4444" />;
    if (type === 'excel' || type === 'xlsx' || type === 'xls') return <FileSpreadsheet size={18} color="#10b981" />;
    if (type === 'eml') return <Mail size={18} color="#3b82f6" />;
    return <FileText size={18} color="#3b82f6" />;
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
          <Loader size={32} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 16px' }} />
          <p>Connecting to RAG backend...</p>
        </div>
      ) : (
        <>
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

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
            {/* Recent Queries Block */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <Clock size={24} color="#3b82f6" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Recent Queries</h3>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>Latest questions asked by your team</p>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {history.length > 0 ? history.map((item, i) => (
                  <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <p style={{ fontWeight: 500, fontSize: '1rem', color: '#1e293b' }}>{item.question}</p>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <FileText size={14} /> {item.sources?.length || 0} sources
                      </span>
                      <span>•</span>
                      <span>{formatTimeAgo(item.created_at)}</span>
                    </div>
                  </div>
                )) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No recent queries found.</p>
                )}
              </div>
            </div>

            {/* Recently Indexed Block */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <Database size={24} color="#3b82f6" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Recently Indexed</h3>
              </div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>Latest documents added to the hub</p>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {documents.length > 0 ? documents.map((doc, i) => (
                  <div key={i} style={{ 
                    display: 'flex', alignItems: 'center', gap: '16px', 
                    padding: '16px', borderRadius: '8px', 
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'white'
                  }}>
                    <div style={{ 
                      padding: '12px', borderRadius: '8px', 
                      backgroundColor: doc.source_type === 'pdf' ? '#fef2f2' : 
                                       doc.source_type === 'excel' || doc.source_type === 'xlsx' ? '#f0fdf4' : 
                                       '#eff6ff'
                    }}>
                      {getSourceIcon(doc.source_type)}
                    </div>
                    <div>
                      <p style={{ fontWeight: 500, fontSize: '0.95rem', color: '#1e293b', marginBottom: '4px' }}>{doc.filename}</p>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        {doc.chunk_count} chunks • {formatTimeAgo(doc.upload_date)}
                      </p>
                    </div>
                  </div>
                )) : (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No documents indexed yet.</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Dashboard;
