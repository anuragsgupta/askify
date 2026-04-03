import React from 'react';

const Reports = () => {
  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '32px', minHeight: '400px' }}>
      <h2 style={{ marginBottom: '16px' }}>System Analytics</h2>
      <p style={{ color: 'var(--text-muted)' }}>
        This module will display RAG query performance, hallucination rates, and popular search topics across the SME knowledge base.
      </p>
    </div>
  );
};

export default Reports;
