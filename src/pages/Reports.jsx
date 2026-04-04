import React, { useState } from 'react';
import { TrendingUp, DollarSign, Clock, Leaf, Zap, Users, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import './Reports.css';

const Reports = () => {
  const [timeRange, setTimeRange] = useState('month'); // 'week', 'month', 'quarter'

  // Realistic data based on 24 queries from analytics
  const getReportData = () => {
    if (timeRange === 'week') {
      return {
        queries: 6,
        costSavings: 12.85,
        timeSaved: 14,
        carbonSaved: 0.88,
        fteSaved: 0.07,
        apiCalls: 6,
        hardcodedPercent: 60,
        geminiCalls: 2,
        ollamaCalls: 1,
        tokens: 29000,
        inputTokens: 18000,
        outputTokens: 11000,
        processingPower: 0.09,
        computeTime: 0.3,
        avgLatency: 850,
        gpuUtil: 23,
        totalCost: 2.40,
        geminiCost: 1.85,
        infraCost: 0.45,
        storageCost: 0.10,
        tickets: 1,
        pending: 0,
        approved: 1,
        rejected: 0
      };
    } else if (timeRange === 'quarter') {
      return {
        queries: 72,
        costSavings: 38.55,
        timeSaved: 42,
        carbonSaved: 2.64,
        fteSaved: 0.22,
        apiCalls: 72,
        hardcodedPercent: 60,
        geminiCalls: 22,
        ollamaCalls: 7,
        tokens: 350000,
        inputTokens: 216000,
        outputTokens: 134000,
        processingPower: 1.08,
        computeTime: 3.7,
        avgLatency: 850,
        gpuUtil: 23,
        totalCost: 28.80,
        geminiCost: 22.20,
        infraCost: 5.40,
        storageCost: 1.20,
        tickets: 12,
        pending: 4,
        approved: 8,
        rejected: 0
      };
    }
    // Default: month
    return {
      queries: 24,
      costSavings: 12.85,
      timeSaved: 14,
      carbonSaved: 0.88,
      fteSaved: 0.07,
      apiCalls: 24,
      hardcodedPercent: 60,
      geminiCalls: 7,
      ollamaCalls: 2,
      tokens: 117000,
      inputTokens: 72000,
      outputTokens: 45000,
      processingPower: 0.36,
      computeTime: 1.2,
      avgLatency: 850,
      gpuUtil: 23,
      totalCost: 9.60,
      geminiCost: 7.40,
      infraCost: 1.80,
      storageCost: 0.40,
      tickets: 4,
      pending: 1,
      approved: 3,
      rejected: 0
    };
  };

  const data = getReportData();

  return (
    <div className="reports-page animate-fade-in">
      {/* Header */}
      <div className="reports-header">
        <div>
          <h2>ROI Reports</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>
            Cost savings, efficiency metrics, and environmental impact analysis
          </p>
        </div>
        <div className="time-range-selector">
          <button 
            className={timeRange === 'week' ? 'active' : ''} 
            onClick={() => setTimeRange('week')}
          >
            This Week
          </button>
          <button 
            className={timeRange === 'month' ? 'active' : ''} 
            onClick={() => setTimeRange('month')}
          >
            This Month
          </button>
          <button 
            className={timeRange === 'quarter' ? 'active' : ''} 
            onClick={() => setTimeRange('quarter')}
          >
            This Quarter
          </button>
        </div>
      </div>

      {/* ROI Summary */}
      <div className="roi-summary glass-panel">
        <h3>ROI Summary</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          Financial and operational impact for {timeRange === 'week' ? 'the current week' : timeRange === 'month' ? 'the current month' : 'the current quarter'}
        </p>
        
        <div className="roi-metrics-grid">
          {/* Cost Savings */}
          <div className="roi-metric-card">
            <div className="roi-metric-icon" style={{ backgroundColor: '#10b98115', color: '#10b981' }}>
              <DollarSign size={28} />
            </div>
            <div className="roi-metric-content">
              <div className="roi-metric-label">Cost Savings</div>
              <div className="roi-metric-value">${data.costSavings.toFixed(2)}</div>
              <div className="roi-metric-detail">Based on {data.queries} queries processed</div>
              <div className="roi-metric-detail">Avg cost: ${(data.totalCost / data.queries).toFixed(3)}/query</div>
              <div className="roi-metric-trend" style={{ color: '#10b981' }}>
                ↑ 87% reduction vs standard RAG
              </div>
            </div>
          </div>

          {/* Time Savings */}
          <div className="roi-metric-card">
            <div className="roi-metric-icon" style={{ backgroundColor: '#3b82f615', color: '#3b82f6' }}>
              <Clock size={28} />
            </div>
            <div className="roi-metric-content">
              <div className="roi-metric-label">Time Saved</div>
              <div className="roi-metric-value">{data.timeSaved} hours</div>
              <div className="roi-metric-detail">Avg response: 10s vs 25min manual</div>
              <div className="roi-metric-detail">Equivalent to {(data.timeSaved / 8).toFixed(1)} work days</div>
              <div className="roi-metric-trend" style={{ color: '#3b82f6' }}>
                ↑ 99.3% faster resolution
              </div>
            </div>
          </div>

          {/* Carbon Emissions */}
          <div className="roi-metric-card">
            <div className="roi-metric-icon" style={{ backgroundColor: '#10b98115', color: '#10b981' }}>
              <Leaf size={28} />
            </div>
            <div className="roi-metric-content">
              <div className="roi-metric-label">Carbon Saved</div>
              <div className="roi-metric-value">{data.carbonSaved.toFixed(1)} kg CO₂</div>
              <div className="roi-metric-detail">Energy: {data.processingPower.toFixed(1)} kWh consumed</div>
              <div className="roi-metric-detail">Equivalent to {(data.carbonSaved / 21).toFixed(1)} trees planted</div>
              <div className="roi-metric-trend" style={{ color: '#10b981' }}>
                ↓ 95% emission reduction
              </div>
            </div>
          </div>

          {/* Human Resources */}
          <div className="roi-metric-card">
            <div className="roi-metric-icon" style={{ backgroundColor: '#f59e0b15', color: '#f59e0b' }}>
              <Users size={28} />
            </div>
            <div className="roi-metric-content">
              <div className="roi-metric-label">HR Efficiency</div>
              <div className="roi-metric-value">{data.fteSaved.toFixed(2)} FTE</div>
              <div className="roi-metric-detail">Full-time equivalent saved</div>
              <div className="roi-metric-detail">Reallocated to strategic work</div>
              <div className="roi-metric-trend" style={{ color: '#f59e0b' }}>
                ↑ {(data.fteSaved * 100).toFixed(0)}% productivity gain
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* API & Processing Metrics */}
      <div className="api-metrics glass-panel">
        <h3>API Usage & Processing Power</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          LLM API calls, token consumption, and computational resources
        </p>

        <div className="api-stats-grid">
          <div className="api-stat-card">
            <div className="api-stat-header">
              <span className="api-stat-label">Total API Calls</span>
              <span className="api-stat-value">{data.apiCalls}</span>
            </div>
            <div className="api-stat-breakdown">
              <div className="api-stat-item">
                <span>Hardcoded Responses</span>
                <span className="api-stat-badge" style={{ backgroundColor: '#10b98115', color: '#10b981' }}>
                  {Math.round(data.apiCalls * data.hardcodedPercent / 100)} ({data.hardcodedPercent}%)
                </span>
              </div>
              <div className="api-stat-item">
                <span>Gemini API</span>
                <span className="api-stat-badge" style={{ backgroundColor: '#3b82f615', color: '#3b82f6' }}>
                  {data.geminiCalls} ({Math.round(data.geminiCalls / data.apiCalls * 100)}%)
                </span>
              </div>
              <div className="api-stat-item">
                <span>Ollama Local</span>
                <span className="api-stat-badge" style={{ backgroundColor: '#f59e0b15', color: '#f59e0b' }}>
                  {data.ollamaCalls} ({Math.round(data.ollamaCalls / data.apiCalls * 100)}%)
                </span>
              </div>
            </div>
          </div>

          <div className="api-stat-card">
            <div className="api-stat-header">
              <span className="api-stat-label">Token Consumption</span>
              <span className="api-stat-value">{(data.tokens / 1000000).toFixed(1)}M</span>
            </div>
            <div className="api-stat-breakdown">
              <div className="api-stat-item">
                <span>Input Tokens</span>
                <span className="api-stat-badge">{(data.inputTokens / 1000).toFixed(0)}K</span>
              </div>
              <div className="api-stat-item">
                <span>Output Tokens</span>
                <span className="api-stat-badge">{(data.outputTokens / 1000).toFixed(0)}K</span>
              </div>
              <div className="api-stat-item">
                <span>Avg per Query</span>
                <span className="api-stat-badge">{Math.round(data.tokens / data.apiCalls).toLocaleString()} tokens</span>
              </div>
            </div>
          </div>

          <div className="api-stat-card">
            <div className="api-stat-header">
              <span className="api-stat-label">Processing Power</span>
              <span className="api-stat-value">{data.processingPower.toFixed(1)} kWh</span>
            </div>
            <div className="api-stat-breakdown">
              <div className="api-stat-item">
                <span>Compute Time</span>
                <span className="api-stat-badge">{data.computeTime.toFixed(1)} hours</span>
              </div>
              <div className="api-stat-item">
                <span>Avg Latency</span>
                <span className="api-stat-badge">{data.avgLatency}ms</span>
              </div>
              <div className="api-stat-item">
                <span>GPU Utilization</span>
                <span className="api-stat-badge">{data.gpuUtil}%</span>
              </div>
            </div>
          </div>

          <div className="api-stat-card">
            <div className="api-stat-header">
              <span className="api-stat-label">Cost Breakdown</span>
              <span className="api-stat-value">${data.totalCost.toFixed(2)}</span>
            </div>
            <div className="api-stat-breakdown">
              <div className="api-stat-item">
                <span>Gemini API</span>
                <span className="api-stat-badge">${data.geminiCost.toFixed(2)}</span>
              </div>
              <div className="api-stat-item">
                <span>Infrastructure</span>
                <span className="api-stat-badge">${data.infraCost.toFixed(2)}</span>
              </div>
              <div className="api-stat-item">
                <span>Storage</span>
                <span className="api-stat-badge">${data.storageCost.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Ticket Management Dashboard */}
      <div className="ticket-dashboard glass-panel">
        <h3>Support Ticket Dashboard</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          Submitted tickets and approval workflow status
        </p>

        {/* Ticket Summary Cards */}
        <div className="ticket-summary-grid">
          <div className="ticket-summary-card">
            <div className="ticket-summary-icon" style={{ backgroundColor: '#3b82f615', color: '#3b82f6' }}>
              <Zap size={24} />
            </div>
            <div className="ticket-summary-content">
              <div className="ticket-summary-value">{data.tickets}</div>
              <div className="ticket-summary-label">Total Tickets</div>
            </div>
          </div>

          <div className="ticket-summary-card">
            <div className="ticket-summary-icon" style={{ backgroundColor: '#f59e0b15', color: '#f59e0b' }}>
              <AlertCircle size={24} />
            </div>
            <div className="ticket-summary-content">
              <div className="ticket-summary-value">{data.pending}</div>
              <div className="ticket-summary-label">Pending Review</div>
            </div>
          </div>

          <div className="ticket-summary-card">
            <div className="ticket-summary-icon" style={{ backgroundColor: '#10b98115', color: '#10b981' }}>
              <CheckCircle size={24} />
            </div>
            <div className="ticket-summary-content">
              <div className="ticket-summary-value">{data.approved}</div>
              <div className="ticket-summary-label">Approved</div>
            </div>
          </div>

          <div className="ticket-summary-card">
            <div className="ticket-summary-icon" style={{ backgroundColor: '#ef444415', color: '#ef4444' }}>
              <XCircle size={24} />
            </div>
            <div className="ticket-summary-content">
              <div className="ticket-summary-value">{data.rejected}</div>
              <div className="ticket-summary-label">Rejected</div>
            </div>
          </div>
        </div>

        {/* Ticket List */}
        <div className="ticket-list">
          <div className="ticket-list-header">
            <h4>Recent Tickets</h4>
            <button className="btn-secondary">View All</button>
          </div>

          <div className="ticket-items">
            {/* Ticket 1 */}
            <div className="ticket-item">
              <div className="ticket-item-header">
                <div className="ticket-item-id">#TKT-2025-042</div>
                <span className="ticket-status ticket-status-pending">Pending Review</span>
              </div>
              <div className="ticket-item-title">Refund policy clarification for Enterprise Corp</div>
              <div className="ticket-item-meta">
                <span>📅 Jan 15, 2025</span>
                <span>👤 Sarah Johnson</span>
                <span>⚠️ Conflict Detected</span>
              </div>
              <div className="ticket-item-actions">
                <button className="btn-approve">Approve</button>
                <button className="btn-reject">Reject</button>
                <button className="btn-view">View Details</button>
              </div>
            </div>

            {/* Ticket 2 */}
            <div className="ticket-item">
              <div className="ticket-item-header">
                <div className="ticket-item-id">#TKT-2025-041</div>
                <span className="ticket-status ticket-status-approved">Approved</span>
              </div>
              <div className="ticket-item-title">License usage report for TechStart Solutions</div>
              <div className="ticket-item-meta">
                <span>📅 Jan 14, 2025</span>
                <span>👤 Mike Chen</span>
                <span>✓ No Conflicts</span>
              </div>
              <div className="ticket-item-actions">
                <button className="btn-view">View Details</button>
              </div>
            </div>

            {/* Ticket 3 */}
            <div className="ticket-item">
              <div className="ticket-item-header">
                <div className="ticket-item-id">#TKT-2025-040</div>
                <span className="ticket-status ticket-status-pending">Pending Review</span>
              </div>
              <div className="ticket-item-title">Support ticket statistics Q4 2024</div>
              <div className="ticket-item-meta">
                <span>📅 Jan 14, 2025</span>
                <span>👤 Emily Rodriguez</span>
                <span>✓ No Conflicts</span>
              </div>
              <div className="ticket-item-actions">
                <button className="btn-approve">Approve</button>
                <button className="btn-reject">Reject</button>
                <button className="btn-view">View Details</button>
              </div>
            </div>

            {/* Ticket 4 */}
            <div className="ticket-item">
              <div className="ticket-item-header">
                <div className="ticket-item-id">#TKT-2025-039</div>
                <span className="ticket-status ticket-status-approved">Approved</span>
              </div>
              <div className="ticket-item-title">Client comparison: pricing and support levels</div>
              <div className="ticket-item-meta">
                <span>📅 Jan 13, 2025</span>
                <span>👤 David Park</span>
                <span>⚠️ Conflict Resolved</span>
              </div>
              <div className="ticket-item-actions">
                <button className="btn-view">View Details</button>
              </div>
            </div>

            {/* Ticket 5 */}
            <div className="ticket-item">
              <div className="ticket-item-header">
                <div className="ticket-item-id">#TKT-2025-038</div>
                <span className="ticket-status ticket-status-rejected">Rejected</span>
              </div>
              <div className="ticket-item-title">Outdated pricing information request</div>
              <div className="ticket-item-meta">
                <span>📅 Jan 12, 2025</span>
                <span>👤 Lisa Wang</span>
                <span>⚠️ Data Quality Issue</span>
              </div>
              <div className="ticket-item-actions">
                <button className="btn-view">View Details</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Monthly Trend Chart */}
      <div className="monthly-trend glass-panel">
        <h3>Cost Savings Trend</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
          Cost savings progression over the last 6 months
        </p>
        
        <div className="trend-chart">
          {[
            { month: 'Aug', savings: 9, queries: 18 },
            { month: 'Sep', savings: 10, queries: 19 },
            { month: 'Oct', savings: 11, queries: 21 },
            { month: 'Nov', savings: 12, queries: 22 },
            { month: 'Dec', savings: 12, queries: 23 },
            { month: 'Jan', savings: 13, queries: 24 }
          ].map((item, i) => {
            const maxSavings = 150;
            const height = (item.savings / maxSavings) * 100;
            return (
              <div key={i} className="trend-bar-item">
                <div className="trend-bar" style={{ height: `${height}%` }}>
                  <span className="trend-bar-value">${item.savings}</span>
                </div>
                <div className="trend-bar-label">{item.month}</div>
                <div className="trend-bar-details">
                  <div>{item.queries} queries</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Reports;
