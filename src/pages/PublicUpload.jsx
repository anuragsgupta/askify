import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { UploadCloud, CheckCircle, AlertCircle, Loader, Box } from 'lucide-react';

const PublicUpload = () => {
  const { token } = useParams();
  const [valid, setValid] = useState(null);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    const validateToken = async () => {
      try {
        const res = await fetch(`/api/share/validate/${token}`);
        if (res.ok) {
          setValid(true);
        } else {
          const data = await res.json();
          setError(data.detail || 'Invalid or expired link.');
          setValid(false);
        }
      } catch (err) {
        setError('Could not connect to server.');
        setValid(false);
      }
    };
    validateToken();
  }, [token]);

  const handleUpload = async (files) => {
    setError('');
    setUploading(true);
    setUploadResult(null);

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`/api/share/upload/${token}`, {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.detail || 'Upload failed');
        }

        const data = await res.json();
        setUploadResult(data);
      } catch (err) {
        setError(err.message);
      }
    }

    setUploading(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length) handleUpload(files);
  };

  if (valid === null) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-color)' }}>
        <Loader size={32} style={{ animation: 'spin 1s linear infinite', color: 'var(--primary-color)' }} />
      </div>
    );
  }

  if (valid === false) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--bg-color)' }}>
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', maxWidth: '500px' }}>
          <AlertCircle size={48} color="var(--error-color)" style={{ margin: '0 auto 16px' }} />
          <h2 style={{ marginBottom: '8px' }}>Invalid Link</h2>
          <p style={{ color: 'var(--text-muted)' }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--bg-color)', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '40px 20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px' }}>
        <Box size={32} color="var(--primary-color)" />
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Askify — Secure Document Upload</h1>
      </div>

      <div style={{ width: '100%', maxWidth: '600px', display: 'flex', flexDirection: 'column', gap: '24px' }}>

        {error && (
          <div style={{ padding: '12px 16px', backgroundColor: 'var(--error-bg)', color: 'var(--error-color)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={18} />
            {error}
          </div>
        )}

        {uploadResult && (
          <div style={{ padding: '16px', backgroundColor: 'var(--success-bg)', color: '#065f46', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <CheckCircle size={20} />
            <span>{uploadResult.message}</span>
          </div>
        )}

        {/* Upload Zone */}
        <div
          className="glass-panel"
          style={{
            padding: '60px 40px',
            border: `2px dashed ${dragOver ? 'var(--success-color)' : 'var(--primary-color)'}`,
            textAlign: 'center',
            cursor: 'pointer',
            backgroundColor: dragOver ? 'rgba(16, 185, 129, 0.05)' : 'white',
            transition: 'all 0.2s',
          }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => document.getElementById('public-file-input').click()}
        >
          <input
            id="public-file-input"
            type="file"
            multiple
            accept=".pdf,.xlsx,.xls,.txt,.eml,.csv"
            style={{ display: 'none' }}
            onChange={(e) => handleUpload(Array.from(e.target.files))}
          />
          {uploading ? (
            <div>
              <Loader size={48} color="var(--primary-color)" style={{ margin: '0 auto 16px', animation: 'spin 1s linear infinite' }} />
              <p style={{ color: 'var(--primary-color)', fontWeight: 500 }}>Parsing and indexing your document...</p>
            </div>
          ) : (
            <>
              <UploadCloud size={56} color="var(--primary-color)" style={{ margin: '0 auto 20px' }} />
              <h3 style={{ marginBottom: '8px', fontSize: '1.25rem' }}>Drop files or click to upload</h3>
              <p style={{ color: 'var(--text-muted)' }}>PDF, Excel, TXT, and EML files supported</p>
            </>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default PublicUpload;
