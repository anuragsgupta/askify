import React, { useState, useEffect } from 'react';
import { Link2, Copy, Check, ExternalLink } from 'lucide-react';

const Settings = () => {
  const [shareLinks, setShareLinks] = useState([]);
  const [creatingLink, setCreatingLink] = useState(false);
  const [copied, setCopied] = useState(null);

  // Folder watch state
  const [watchedFolders, setWatchedFolders] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [newFolderPath, setNewFolderPath] = useState('');
  const [scanning, setScanning] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchShareLinks();
    fetchWatchedFolders();
    fetchStatistics();
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

  const fetchWatchedFolders = async () => {
    try {
      const res = await fetch('/api/folder-watch/list');
      const data = await res.json();
      setWatchedFolders(data.folders || []);
    } catch (err) {
      console.error('Failed to fetch watched folders:', err);
    }
  };

  const fetchStatistics = async () => {
    try {
      const res = await fetch('/api/folder-watch/statistics');
      const data = await res.json();
      setStatistics(data);
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    }
  };

  const addFolder = async () => {
    if (!newFolderPath.trim()) {
      setError('Please enter a folder path');
      return;
    }

    try {
      const res = await fetch('/api/folder-watch/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_path: newFolderPath })
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.message || 'Failed to add folder');
        return;
      }

      setNewFolderPath('');
      setError(null);
      fetchWatchedFolders();
      fetchStatistics();
    } catch (err) {
      setError('Network error: ' + err.message);
    }
  };

  const removeFolder = async (folderPath) => {
    try {
      const res = await fetch('/api/folder-watch/remove', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_path: folderPath })
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.message || 'Failed to remove folder');
        return;
      }

      setError(null);
      fetchWatchedFolders();
      fetchStatistics();
    } catch (err) {
      setError('Network error: ' + err.message);
    }
  };

  const scanFolder = async (folderPath) => {
    setScanning({ ...scanning, [folderPath]: true });
    setError(null);

    try {
      const res = await fetch('/api/folder-watch/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_path: folderPath })
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.message || 'Failed to scan folder');
        setScanning({ ...scanning, [folderPath]: false });
        return;
      }

      // Show scan results as a temporary success message
      setError(null);
      alert(data.message || `Scan complete: ${data.ingested} ingested, ${data.duplicates} duplicates, ${data.errors} errors`);
      
      fetchWatchedFolders();
      fetchStatistics();
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setScanning({ ...scanning, [folderPath]: false });
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

      {/* Folder Watch Section */}
      <div className="glass-panel" style={{ padding: '32px' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '24px' }}>Folder Watch</h2>
        
        <p style={{ color: 'var(--text-muted)', marginBottom: '20px', fontSize: '0.9rem' }}>
          Monitor folders for new documents and automatically ingest them into your knowledge base.
        </p>

        {/* Error Display */}
        {error && (
          <div style={{ 
            padding: '12px 16px', 
            backgroundColor: '#fee', 
            border: '1px solid #fcc',
            borderRadius: '8px', 
            color: '#c33',
            marginBottom: '16px',
            fontSize: '0.9rem'
          }}>
            {error}
          </div>
        )}

        {/* Add Folder Input */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
          <input
            type="text"
            value={newFolderPath}
            onChange={(e) => setNewFolderPath(e.target.value)}
            placeholder="Enter folder path (e.g., /path/to/documents)"
            style={{
              flex: 1,
              padding: '10px 14px',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              fontSize: '0.9rem'
            }}
            onKeyPress={(e) => e.key === 'Enter' && addFolder()}
          />
          <button className="btn-primary" onClick={addFolder}>
            Add Folder
          </button>
        </div>

        {/* Watched Folders List */}
        {watchedFolders.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '24px' }}>
            No folders being watched. Add a folder to start monitoring.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {watchedFolders.map((folder) => (
              <div key={folder.id} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 16px',
                backgroundColor: '#f9fafb',
                borderRadius: '8px',
                border: '1px solid var(--border-color-light)',
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '0.9rem', fontWeight: 500, marginBottom: '4px' }}>
                    {folder.folder_path}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Added {new Date(folder.created_at).toLocaleDateString()}
                    {folder.last_scan && ` • Last scan: ${new Date(folder.last_scan).toLocaleString()}`}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '8px', marginLeft: '12px' }}>
                  <button
                    className="btn-secondary"
                    onClick={() => scanFolder(folder.folder_path)}
                    disabled={scanning[folder.folder_path]}
                    style={{ fontSize: '0.85rem', padding: '6px 12px' }}
                  >
                    {scanning[folder.folder_path] ? 'Scanning...' : 'Scan Now'}
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => removeFolder(folder.folder_path)}
                    style={{ fontSize: '0.85rem', padding: '6px 12px', color: '#c33' }}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Statistics Section */}
      {statistics && (
        <div className="glass-panel" style={{ padding: '32px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '24px' }}>Ingestion Statistics</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{ padding: '16px', backgroundColor: '#f0fdf4', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.85rem', color: '#059669', marginBottom: '4px' }}>Total Files</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 600, color: '#047857' }}>{statistics.total_files}</div>
            </div>
            <div style={{ padding: '16px', backgroundColor: '#fef3c7', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.85rem', color: '#d97706', marginBottom: '4px' }}>Duplicates Detected</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 600, color: '#b45309' }}>{statistics.total_duplicates}</div>
            </div>
          </div>

          {statistics.files_by_type && statistics.files_by_type.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Files by Type</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {statistics.files_by_type.map((item) => (
                  <div key={item.type} style={{
                    padding: '8px 12px',
                    backgroundColor: '#f3f4f6',
                    borderRadius: '6px',
                    fontSize: '0.85rem'
                  }}>
                    <span style={{ fontWeight: 600 }}>{item.type}</span>: {item.count}
                  </div>
                ))}
              </div>
            </div>
          )}

          {statistics.recent_ingestions && statistics.recent_ingestions.length > 0 && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '12px' }}>Recent Ingestions</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {statistics.recent_ingestions.map((ingestion, index) => (
                  <div key={index} style={{
                    padding: '12px 14px',
                    backgroundColor: '#f9fafb',
                    borderRadius: '6px',
                    border: '1px solid var(--border-color-light)',
                    fontSize: '0.85rem'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <div style={{ 
                        fontWeight: 500, 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis', 
                        whiteSpace: 'nowrap',
                        flex: 1,
                        marginRight: '12px'
                      }}>
                        {ingestion.file_path.split('/').pop()}
                      </div>
                      <div style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 500,
                        backgroundColor: ingestion.status === 'success' ? '#d1fae5' : ingestion.status === 'skipped_duplicate' ? '#fef3c7' : '#fee2e2',
                        color: ingestion.status === 'success' ? '#065f46' : ingestion.status === 'skipped_duplicate' ? '#92400e' : '#991b1b'
                      }}>
                        {ingestion.status === 'success' ? 'Success' : ingestion.status === 'skipped_duplicate' ? 'Duplicate' : 'Failed'}
                      </div>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {ingestion.chunks_created > 0 && `${ingestion.chunks_created} chunks • `}
                      {new Date(ingestion.timestamp).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Settings;
