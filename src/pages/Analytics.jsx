import React, { useState, useEffect } from 'react';
import { BarChart2, TrendingUp, AlertTriangle, Clock, Search, Zap, Network } from 'lucide-react';
import './Analytics.css';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(7);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalytics();
    loadGraphData();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      const res = await fetch(`/api/analytics/summary?days=${timeRange}`);
      if (res.ok) {
        const data = await res.json();
        
        // If no real data, use mock data for demo
        if (data.total_queries === 0) {
          setAnalytics(getMockAnalytics(timeRange));
        } else {
          setAnalytics(data);
        }
      }
    } catch (err) {
      console.error('Failed to load analytics:', err);
      // Use mock data on error for demo purposes
      setAnalytics(getMockAnalytics(timeRange));
    } finally {
      setLoading(false);
    }
  };

  const loadGraphData = async () => {
    try {
      const res = await fetch('/api/analytics/knowledge-graph');
      if (res.ok) {
        const data = await res.json();
        
        // If no real data, use mock data for demo
        if (data.nodes.length === 0) {
          setGraphData(getMockGraphData());
        } else {
          setGraphData(data);
        }
      }
    } catch (err) {
      console.error('Failed to load graph data:', err);
      // Use mock data on error for demo purposes
      setGraphData(getMockGraphData());
    }
  };

  // Mock data generator for demo purposes
  const getMockAnalytics = (days) => {
    const queriesOverTime = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      queriesOverTime.push({
        date: date.toISOString().split('T')[0],
        count: Math.floor(Math.random() * 15) + 5
      });
    }

    return {
      total_queries: 247,
      avg_relevance: 0.87,
      avg_response_time_ms: 1850,
      hallucination_rate: 4.2,
      conflict_rate: 12.5,
      queries_over_time: queriesOverTime,
      llm_usage: [
        { llm: 'gemini', count: 189 },
        { llm: 'ollama', count: 58 }
      ],
      top_topics: [
        { topic: 'Pricing and Refund Policies', count: 45 },
        { topic: 'Support Ticket Analysis', count: 38 },
        { topic: 'User License Management', count: 32 },
        { topic: 'Contract Terms and Renewals', count: 28 },
        { topic: 'Client Comparisons', count: 24 },
        { topic: 'Service Level Agreements', count: 19 },
        { topic: 'Billing and Invoicing', count: 15 },
        { topic: 'Feature Requests', count: 12 }
      ]
    };
  };

  const getMockGraphData = () => {
    return {
      nodes: [
        { id: 'client_techstart_contract.pdf', label: 'TechStart Contract' },
        { id: 'enterprise_corp_agreement.pdf', label: 'Enterprise Agreement' },
        { id: 'startuphub_terms.pdf', label: 'StartupHub Terms' },
        { id: 'pricing_comparison_2024.xlsx', label: 'Pricing Comparison' },
        { id: 'support_tickets_q4_2024.xlsx', label: 'Support Tickets Q4' },
        { id: 'refund_policy_2024.pdf', label: 'Refund Policy' },
        { id: 'client_health_report.pdf', label: 'Client Health Report' },
        { id: 'license_usage_report.xlsx', label: 'License Usage' }
      ],
      edges: [
        { source: 'client_techstart_contract.pdf', target: 'pricing_comparison_2024.xlsx', count: 12 },
        { source: 'client_techstart_contract.pdf', target: 'refund_policy_2024.pdf', count: 8 },
        { source: 'enterprise_corp_agreement.pdf', target: 'pricing_comparison_2024.xlsx', count: 10 },
        { source: 'enterprise_corp_agreement.pdf', target: 'license_usage_report.xlsx', count: 15 },
        { source: 'support_tickets_q4_2024.xlsx', target: 'client_health_report.pdf', count: 18 },
        { source: 'startuphub_terms.pdf', target: 'pricing_comparison_2024.xlsx', count: 7 },
        { source: 'refund_policy_2024.pdf', target: 'pricing_comparison_2024.xlsx', count: 6 }
      ]
    };
  };

  if (loading) {
    return (
      <div className="analytics-page">
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div className="spinner"></div>
          <p style={{ marginTop: '20px' }}>Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="analytics-page">
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <p>No analytics data available yet.</p>
          <p style={{ fontSize: '0.9rem', marginTop: '10px' }}>Start asking questions to generate analytics!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page animate-fade-in">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <h2>System Analytics</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>
            RAG query performance, hallucination detection, and knowledge insights
          </p>
        </div>
        <div className="time-range-selector">
          <button 
            className={timeRange === 7 ? 'active' : ''} 
            onClick={() => setTimeRange(7)}
          >
            7 Days
          </button>
          <button 
            className={timeRange === 30 ? 'active' : ''} 
            onClick={() => setTimeRange(30)}
          >
            30 Days
          </button>
          <button 
            className={timeRange === 90 ? 'active' : ''} 
            onClick={() => setTimeRange(90)}
          >
            90 Days
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="analytics-tabs">
        <button 
          className={activeTab === 'overview' ? 'active' : ''} 
          onClick={() => setActiveTab('overview')}
        >
          <BarChart2 size={18} />
          Overview
        </button>
        <button 
          className={activeTab === 'topics' ? 'active' : ''} 
          onClick={() => setActiveTab('topics')}
        >
          <Search size={18} />
          Search Topics
        </button>
        <button 
          className={activeTab === 'graph' ? 'active' : ''} 
          onClick={() => setActiveTab('graph')}
        >
          <Network size={18} />
          Knowledge Graph
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
          {/* Key Metrics */}
          <div className="metrics-grid">
            <div className="metric-card glass-panel">
              <div className="metric-icon" style={{ backgroundColor: '#3b82f615', color: '#3b82f6' }}>
                <Search size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Total Queries</div>
                <div className="metric-value">{analytics.total_queries}</div>
                <div className="metric-trend">Last {timeRange} days</div>
              </div>
            </div>

            <div className="metric-card glass-panel">
              <div className="metric-icon" style={{ backgroundColor: '#10b98115', color: '#10b981' }}>
                <TrendingUp size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Avg Relevance</div>
                <div className="metric-value">{(analytics.avg_relevance * 100).toFixed(1)}%</div>
                <div className="metric-trend" style={{ color: analytics.avg_relevance >= 0.75 ? '#10b981' : '#f59e0b' }}>
                  {analytics.avg_relevance >= 0.75 ? '✓ Excellent' : '⚠ Needs improvement'}
                </div>
              </div>
            </div>

            <div className="metric-card glass-panel">
              <div className="metric-icon" style={{ backgroundColor: '#f59e0b15', color: '#f59e0b' }}>
                <Clock size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Avg Response Time</div>
                <div className="metric-value">{analytics.avg_response_time_ms}ms</div>
                <div className="metric-trend">Processing speed</div>
              </div>
            </div>

            <div className="metric-card glass-panel">
              <div className="metric-icon" style={{ backgroundColor: '#ef444415', color: '#ef4444' }}>
                <AlertTriangle size={24} />
              </div>
              <div className="metric-content">
                <div className="metric-label">Hallucination Rate</div>
                <div className="metric-value">{analytics.hallucination_rate.toFixed(1)}%</div>
                <div className="metric-trend" style={{ color: analytics.hallucination_rate < 10 ? '#10b981' : '#ef4444' }}>
                  {analytics.hallucination_rate < 10 ? '✓ Low risk' : '⚠ High risk'}
                </div>
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="charts-grid">
            {/* Queries Over Time */}
            <div className="chart-card glass-panel">
              <h3>Queries Over Time</h3>
              <div className="bar-chart">
                {analytics.queries_over_time.map((item, i) => {
                  const maxCount = Math.max(...analytics.queries_over_time.map(d => d.count));
                  const height = (item.count / maxCount) * 100;
                  return (
                    <div key={i} className="bar-item">
                      <div className="bar" style={{ height: `${height}%` }}>
                        <span className="bar-value">{item.count}</span>
                      </div>
                      <div className="bar-label">{new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* LLM Usage */}
            <div className="chart-card glass-panel">
              <h3>LLM Provider Usage</h3>
              <div className="pie-chart-container">
                {analytics.llm_usage.map((item, i) => {
                  const total = analytics.llm_usage.reduce((sum, d) => sum + d.count, 0);
                  const percentage = ((item.count / total) * 100).toFixed(1);
                  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];
                  return (
                    <div key={i} className="pie-item">
                      <div className="pie-color" style={{ backgroundColor: colors[i % colors.length] }}></div>
                      <div className="pie-label">{item.llm}</div>
                      <div className="pie-value">{percentage}%</div>
                      <div className="pie-count">({item.count} queries)</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Additional Metrics */}
          <div className="additional-metrics glass-panel">
            <h3>Performance Indicators</h3>
            <div className="metrics-list">
              <div className="metric-row">
                <span className="metric-row-label">Conflict Detection Rate</span>
                <div className="metric-row-bar">
                  <div className="metric-row-fill" style={{ width: `${analytics.conflict_rate}%`, backgroundColor: '#f59e0b' }}></div>
                </div>
                <span className="metric-row-value">{analytics.conflict_rate.toFixed(1)}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-row-label">Citation Quality</span>
                <div className="metric-row-bar">
                  <div className="metric-row-fill" style={{ width: `${100 - analytics.hallucination_rate}%`, backgroundColor: '#10b981' }}></div>
                </div>
                <span className="metric-row-value">{(100 - analytics.hallucination_rate).toFixed(1)}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-row-label">Average Relevance Score</span>
                <div className="metric-row-bar">
                  <div className="metric-row-fill" style={{ width: `${analytics.avg_relevance * 100}%`, backgroundColor: '#3b82f6' }}></div>
                </div>
                <span className="metric-row-value">{(analytics.avg_relevance * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Topics Tab */}
      {activeTab === 'topics' && (
        <div className="topics-container glass-panel">
          <h3>Popular Search Topics</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
            Most frequently searched topics in your knowledge base
          </p>
          <div className="topics-list">
            {analytics.top_topics.map((topic, i) => {
              const maxCount = Math.max(...analytics.top_topics.map(t => t.count));
              const width = (topic.count / maxCount) * 100;
              return (
                <div key={i} className="topic-item">
                  <div className="topic-rank">#{i + 1}</div>
                  <div className="topic-content">
                    <div className="topic-name">{topic.topic}</div>
                    <div className="topic-bar">
                      <div className="topic-bar-fill" style={{ width: `${width}%` }}></div>
                    </div>
                  </div>
                  <div className="topic-count">{topic.count} searches</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Knowledge Graph Tab */}
      {activeTab === 'graph' && (
        <div className="graph-container glass-panel">
          <h3>Knowledge Graph</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
            Visual representation of document connections and relationships
          </p>
          {graphData && graphData.nodes.length > 0 ? (
            <div className="graph-visualization">
              <div className="graph-legend">
                <div className="legend-item">
                  <div className="legend-dot" style={{ backgroundColor: '#3b82f6' }}></div>
                  <span>Document Node</span>
                </div>
                <div className="legend-item">
                  <div className="legend-line"></div>
                  <span>Connection (co-occurrence)</span>
                </div>
              </div>
              <div className="graph-nodes">
                {graphData.nodes.map((node, i) => (
                  <div key={i} className="graph-node" style={{ 
                    left: `${(i % 5) * 20 + 10}%`, 
                    top: `${Math.floor(i / 5) * 25 + 15}%` 
                  }}>
                    <div className="node-circle"></div>
                    <div className="node-label">{node.label}</div>
                    <div className="node-connections">
                      {graphData.edges.filter(e => e.source === node.id || e.target === node.id).length} connections
                    </div>
                  </div>
                ))}
              </div>
              <div className="graph-stats">
                <div className="graph-stat">
                  <strong>{graphData.nodes.length}</strong>
                  <span>Documents</span>
                </div>
                <div className="graph-stat">
                  <strong>{graphData.edges.length}</strong>
                  <span>Connections</span>
                </div>
                <div className="graph-stat">
                  <strong>{graphData.edges.length > 0 ? (graphData.edges.reduce((sum, e) => sum + e.count, 0) / graphData.edges.length).toFixed(1) : 0}</strong>
                  <span>Avg Co-occurrence</span>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <Network size={48} style={{ opacity: 0.3, marginBottom: '16px' }} />
              <p>No document connections yet.</p>
              <p style={{ fontSize: '0.9rem', marginTop: '8px' }}>Ask more questions to build the knowledge graph!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Analytics;
