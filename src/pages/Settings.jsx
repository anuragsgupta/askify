import React, { useState, useEffect } from 'react';
import { Link2, Copy, Check, ExternalLink } from 'lucide-react';

const Settings = () => {
  const [shareLinks, setShareLinks] = useState([]);
  const [creatingLink, setCreatingLink] = useState(false);
  const [copied, setCopied] = useState(null);

  useEffect(() => {
    fetchShareLinks();
  }, []);

  const fetchShareLinks = async () => {
    try {
      const res = await fetch('/api/share/list');
      const data = await res.json();
      setShareLinks(data.links || []);
    } catch (err) {
      console.error('Failed to fetch share links:', err);
    }
  };

  const createShareLink = async () => {
    setCreatingLink(true);
    try {
      const res = await fetch('/api/share/create', { method: 'POST' });
      await res.json();
      fetchShareLinks();
    } catch (err) {
      console.error('Failed to create share link:', err);
    }
    setCreatingLink(false);
  };

  const copyLink = (token) => {
    const url = `${window.location.origin}/upload/${token}`;
    navigator.clipboard.writeText(url);
    setCopied(token);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* Shareable Upload Links Section */}
      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ padding: '8px', backgroundColor: '#f0fdf4', borderRadius: '8px', color: '#10b981' }}>
              <Link2 size={20} />
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Shareable Upload Links</h2>
          </div>
          <button className="btn-primary" onClick={createShareLink} disabled={creatingLink}>
            {creatingLink ? 'Creating...' : '+ Generate Link'}
          </button>
        </div>

        <p style={{ color: 'var(--text-muted)', marginBottom: '20px', fontSize: '0.9rem' }}>
          Share these links with anyone so they can upload documents directly into your knowledge base. Links expire after 7 days.
        </p>

        {shareLinks.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '24px' }}>
            No share links created yet. Click "Generate Link" to create one.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {shareLinks.map((link) => {
              const fullUrl = `${window.location.origin}/upload/${link.token}`;
              return (
                <div key={link.token} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '14px 16px', backgroundColor: '#f9fafb', borderRadius: '8px',
                  border: '1px solid var(--border-color-light)',
                }}>
                  <div style={{ flex: 1, overflow: 'hidden' }}>
                    <code style={{ fontSize: '0.8rem', color: 'var(--primary-color)', wordBreak: 'break-all' }}>{fullUrl}</code>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      Used {link.uses} time{link.uses !== 1 ? 's' : ''} • Expires {new Date(link.expires).toLocaleDateString()}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', marginLeft: '12px' }}>
                    <button onClick={() => copyLink(link.token)} style={{ padding: '6px', color: copied === link.token ? 'var(--success-color)' : 'var(--text-muted)' }}>
                      {copied === link.token ? <Check size={16} /> : <Copy size={16} />}
                    </button>
                    <a href={fullUrl} target="_blank" rel="noopener noreferrer" style={{ padding: '6px', color: 'var(--text-muted)' }}>
                      <ExternalLink size={16} />
                    </a>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default Settings;
