import React from 'react';

const Settings = () => {
  return (
    <div className="glass-panel animate-fade-in" style={{ padding: '32px', minHeight: '400px' }}>
      <h2 style={{ marginBottom: '16px' }}>RAG Configuration Options</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
        Adjust embed model thresholds, generation temperature, and access controls.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '400px' }}>
         <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <span>Auto-Conflict Detection</span>
            <input type="checkbox" defaultChecked />
         </div>
         <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <span>Strict Temporal Prioritization</span>
            <input type="checkbox" defaultChecked />
         </div>
      </div>
    </div>
  );
};

export default Settings;
