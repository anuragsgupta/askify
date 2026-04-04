import React, { useState, useEffect, useCallback } from 'react';
import { UploadCloud, File, FileSpreadsheet, Mail, CheckCircle, Trash2, Loader, AlertCircle, Globe, Link as LinkIcon } from 'lucide-react';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState('');
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [isScrapingUrl, setIsScrapingUrl] = useState(false);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await fetch('/api/documents');
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleUpload = async (files) => {
    setError('');
    setIsUploading(true);

    for (const file of files) {
      setUploadProgress(`Ingesting "${file.name}"... Parsing → Embedding → Indexing`);
      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || 'Upload failed');
        }

        const data = await res.json();
        setUploadProgress(`✓ ${data.message}`);
      } catch (err) {
        setError(`Failed to upload "${file.name}": ${err.message}`);
      }
    }

    setIsUploading(false);
    setUploadProgress('');
    fetchDocuments();
  };

  const handleDelete = async (docId) => {
    try {
      await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
      fetchDocuments();
    } catch (err) {
      setError('Failed to delete document.');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length) handleUpload(files);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    if (files.length) handleUpload(files);
  };

  const getIcon = (type) => {
    if (type === 'pdf') return File;
    if (type === 'xlsx' || type === 'xls' || type === 'excel') return FileSpreadsheet;
    if (type === 'web') return Globe;
    return Mail;
  };

  const getColor = (type) => {
    if (type === 'pdf') return '#ef4444';
    if (type === 'xlsx' || type === 'xls' || type === 'excel') return '#10b981';
    if (type === 'web') return '#8b5cf6';
    return '#3b82f6';
  };

  const handleUrlUpload = async (e) => {
    e.preventDefault();
    if (!urlInput.trim() || isScrapingUrl) return;

    setError('');
    setIsScrapingUrl(true);
    setUploadProgress(`Scraping website: ${urlInput}... Extracting content → Embedding → Indexing`);

    try {
      const res = await fetch('/api/upload-url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: urlInput }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'URL upload failed');
      }

      const data = await res.json();
      setUploadProgress(`✓ ${data.message}`);
      setUrlInput('');
      setTimeout(() => {
        setUploadProgress('');
        fetchDocuments();
      }, 2000);
    } catch (err) {
      setError(`Failed to scrape URL: ${err.message}`);
      setUploadProgress('');
    }

    setIsScrapingUrl(false);
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {error && (
        <div style={{ padding: '12px 16px', backgroundColor: 'var(--error-bg)', color: 'var(--error-color)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={18} />
          {error}
          <button onClick={() => setError('')} style={{ marginLeft: 'auto', fontWeight: 600 }}>×</button>
        </div>
      )}

      {/* Upload Zone */}
      <div
        className="glass-panel"
        style={{
          padding: '40px',
          border: `2px dashed ${dragOver ? 'var(--success-color)' : 'var(--primary-color)'}`,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: dragOver ? 'rgba(16, 185, 129, 0.05)' : 'rgba(59, 130, 246, 0.02)',
          transition: 'all 0.2s',
        }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          multiple
          accept=".pdf,.xlsx,.xls,.txt,.eml,.csv"
          style={{ display: 'none' }}
          onChange={handleFileInput}
        />
        {isUploading ? (
          <div>
            <Loader size={48} color="var(--primary-color)" style={{ margin: '0 auto 16px', animation: 'spin 1s linear infinite' }} />
            <p style={{ color: 'var(--primary-color)', fontWeight: 500 }}>{uploadProgress}</p>
          </div>
        ) : (
          <>
            <UploadCloud size={48} color="var(--primary-color)" style={{ margin: '0 auto 16px' }} />
            <h3 style={{ marginBottom: '8px' }}>Drag & Drop documents here, or click to browse</h3>
            <p style={{ color: 'var(--text-muted)' }}>Supports PDF, Excel (.xlsx), plain text (.txt), and email (.eml) files.</p>
          </>
        )}
      </div>

      {/* URL Upload Section */}
      <div className="glass-panel" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div style={{ 
            padding: '10px', 
            backgroundColor: '#f3e8ff', 
            borderRadius: '8px', 
            color: '#8b5cf6' 
          }}>
            <Globe size={24} />
          </div>
          <div>
            <h3 style={{ margin: 0, marginBottom: '4px' }}>Ingest from Website</h3>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Enter a URL to scrape and index website content
            </p>
          </div>
        </div>

        <form onSubmit={handleUrlUpload} style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <LinkIcon 
              size={18} 
              style={{ 
                position: 'absolute', 
                left: '14px', 
                top: '50%', 
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)'
              }} 
            />
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://example.com/article"
              disabled={isScrapingUrl}
              style={{
                width: '100%',
                padding: '12px 14px 12px 42px',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                fontSize: '0.9rem',
                backgroundColor: 'var(--bg-primary)',
              }}
              required
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            disabled={isScrapingUrl || !urlInput.trim()}
            style={{
              padding: '12px 24px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              minWidth: '140px',
              justifyContent: 'center'
            }}
          >
            {isScrapingUrl ? (
              <>
                <Loader size={18} style={{ animation: 'spin 1s linear infinite' }} />
                Scraping...
              </>
            ) : (
              <>
                <Globe size={18} />
                Ingest URL
              </>
            )}
          </button>
        </form>

        {isScrapingUrl && uploadProgress && (
          <div style={{ 
            marginTop: '16px', 
            padding: '12px', 
            backgroundColor: '#f0f9ff', 
            borderRadius: '8px',
            fontSize: '0.85rem',
            color: '#0369a1'
          }}>
            {uploadProgress}
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ fontWeight: 600 }}>Ingested Knowledge Base</h3>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{documents.length} document{documents.length !== 1 ? 's' : ''}</span>
        </div>

        {documents.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '32px' }}>
            No documents ingested yet. Upload a file to get started.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {documents.map((doc) => {
              const Icon = getIcon(doc.source_type);
              const color = getColor(doc.source_type);
              return (
                <div key={doc.doc_id} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '16px', backgroundColor: '#f9fafb', borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-color-light)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <Icon size={24} color={color} />
                    <div>
                      <h4 style={{ fontWeight: 500 }}>{doc.filename}</h4>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {doc.chunk_count} chunks • {doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : 'Unknown date'}
                      </span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success-color)', fontSize: '0.875rem' }}>
                      <CheckCircle size={16} />
                      {doc.status}
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(doc.doc_id); }}
                      style={{ color: 'var(--text-muted)', padding: '4px' }}
                      title="Delete document"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default Documents;
