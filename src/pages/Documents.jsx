import React, { useState } from 'react';
import { UploadCloud, File, FileSpreadsheet, Mail, CheckCircle } from 'lucide-react';

const Documents = () => {
  const [isUploading, setIsUploading] = useState(false);

  const mockUpload = () => {
    setIsUploading(true);
    setTimeout(() => setIsUploading(false), 2000);
  };

  const docs = [
    { name: 'Q1_Pricing_Sheet.xlsx', type: 'excel', icon: FileSpreadsheet, date: 'Mar 12', status: 'Indexed' },
    { name: 'Refund_Policy_2024.pdf', type: 'pdf', icon: File, date: 'Mar 01', status: 'Indexed' },
    { name: 'FWD: Acme Corp Bulk Query', type: 'email', icon: Mail, date: 'Feb 20', status: 'Indexed' },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div 
        className="glass-panel" 
        style={{ 
          padding: '40px', 
          border: '2px dashed var(--primary-color)', 
          textAlign: 'center', 
          cursor: 'pointer',
          backgroundColor: 'rgba(59, 130, 246, 0.02)'
        }}
        onClick={mockUpload}
      >
        <UploadCloud size={48} color="var(--primary-color)" style={{ margin: '0 auto 16px' }} />
        <h3 style={{ marginBottom: '8px' }}>Drag & Drop unstructured documents</h3>
        <p style={{ color: 'var(--text-muted)' }}>Supports PDFs, Excel spreadsheets, and raw text/email files.</p>
        {isUploading && (
          <div style={{ marginTop: '16px', color: 'var(--primary-color)', fontWeight: 500 }}>
             Extracting text & tabular data... chunking into Vector DB...
          </div>
        )}
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ marginBottom: '20px', fontWeight: 600 }}>Ingested Knowledge Base</h3>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {docs.map((doc, idx) => (
            <div key={idx} style={{ 
              display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
              padding: '16px', backgroundColor: '#f9fafb', borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-color-light)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <doc.icon 
                  size={24} 
                  color={doc.type === 'excel' ? '#10b981' : doc.type === 'pdf' ? '#ef4444' : '#3b82f6'} 
                />
                <div>
                  <h4 style={{ fontWeight: 500 }}>{doc.name}</h4>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Added {doc.date}</span>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--success-color)', fontSize: '0.875rem' }}>
                <CheckCircle size={16} />
                {doc.status}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Documents;
