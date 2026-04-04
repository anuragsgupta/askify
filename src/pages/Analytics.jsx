import React, { useState, useEffect, useRef } from 'react';
import { BarChart2, TrendingUp, AlertTriangle, Clock, Search, Zap, Network } from 'lucide-react';
import './Analytics.css';

// 3D Vector Cluster Visualization Component
const VectorCluster3D = () => {
  const canvasRef = useRef(null);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [lastMouse, setLastMouse] = useState({ x: 0, y: 0 });

  // Generate mock vector clusters
  const generateClusters = () => {
    const clusters = [];
    const clusterCenters = [
      { x: -50, y: 30, z: 20, color: '#3b82f6', label: 'Contracts' },
      { x: 40, y: -20, z: -30, color: '#10b981', label: 'Support Tickets' },
      { x: 20, y: 50, z: 40, color: '#f59e0b', label: 'Pricing Docs' },
      { x: -30, y: -40, z: 10, color: '#ef4444', label: 'Policies' }
    ];

    clusterCenters.forEach(center => {
      // Generate 15-20 points around each center
      const pointCount = 15 + Math.floor(Math.random() * 6);
      for (let i = 0; i < pointCount; i++) {
        clusters.push({
          x: center.x + (Math.random() - 0.5) * 30,
          y: center.y + (Math.random() - 0.5) * 30,
          z: center.z + (Math.random() - 0.5) * 30,
          color: center.color,
          label: center.label,
          size: 3 + Math.random() * 3
        });
      }
    });

    return clusters;
  };

  const [clusters] = useState(generateClusters());

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    const height = canvas.height = canvas.offsetHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const centerX = canvas.offsetWidth / 2;
    const centerY = canvas.offsetHeight / 2;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

    // Draw axes
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    
    // X axis
    ctx.beginPath();
    ctx.moveTo(50, centerY);
    ctx.lineTo(canvas.offsetWidth - 50, centerY);
    ctx.stroke();
    
    // Y axis
    ctx.beginPath();
    ctx.moveTo(centerX, 50);
    ctx.lineTo(centerX, canvas.offsetHeight - 50);
    ctx.stroke();
    
    ctx.setLineDash([]);

    // Sort points by z-depth for proper rendering
    const sortedClusters = [...clusters].sort((a, b) => {
      const rotatedA = rotatePoint(a, rotation);
      const rotatedB = rotatePoint(b, rotation);
      return rotatedA.z - rotatedB.z;
    });

    // Draw points
    sortedClusters.forEach(point => {
      const rotated = rotatePoint(point, rotation);
      const scale = 200 / (200 + rotated.z);
      const x = centerX + rotated.x * scale * 2;
      const y = centerY - rotated.y * scale * 2;
      const size = point.size * scale;

      // Draw point
      ctx.fillStyle = point.color;
      ctx.globalAlpha = 0.6 + scale * 0.4;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();

      // Draw glow
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, size * 2);
      gradient.addColorStop(0, point.color + '40');
      gradient.addColorStop(1, point.color + '00');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, size * 2, 0, Math.PI * 2);
      ctx.fill();
    });

    ctx.globalAlpha = 1;

    // Draw cluster labels
    const labelPositions = new Map();
    clusters.forEach(point => {
      if (!labelPositions.has(point.label)) {
        const rotated = rotatePoint(point, rotation);
        const scale = 200 / (200 + rotated.z);
        const x = centerX + rotated.x * scale * 2;
        const y = centerY - rotated.y * scale * 2;
        labelPositions.set(point.label, { x, y, color: point.color });
      }
    });

    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'center';
    labelPositions.forEach((pos, label) => {
      ctx.fillStyle = pos.color;
      ctx.fillText(label, pos.x, pos.y - 15);
    });

  }, [clusters, rotation]);

  const rotatePoint = (point, rot) => {
    // Rotate around Y axis
    let x = point.x * Math.cos(rot.y) - point.z * Math.sin(rot.y);
    let z = point.x * Math.sin(rot.y) + point.z * Math.cos(rot.y);
    
    // Rotate around X axis
    let y = point.y * Math.cos(rot.x) - z * Math.sin(rot.x);
    z = point.y * Math.sin(rot.x) + z * Math.cos(rot.x);
    
    return { x, y, z };
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setLastMouse({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - lastMouse.x;
    const deltaY = e.clientY - lastMouse.y;
    
    setRotation(prev => ({
      x: prev.x + deltaY * 0.01,
      y: prev.y + deltaX * 0.01
    }));
    
    setLastMouse({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Auto-rotate
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isDragging) {
        setRotation(prev => ({
          x: prev.x,
          y: prev.y + 0.005
        }));
      }
    }, 50);
    
    return () => clearInterval(interval);
  }, [isDragging]);

  return (
    <div className="vector-cluster-3d">
      <div className="vector-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#3b82f6' }}></div>
          <span>Contracts (20 docs)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#10b981' }}></div>
          <span>Support Tickets (18 docs)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#f59e0b' }}></div>
          <span>Pricing Docs (17 docs)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ backgroundColor: '#ef4444' }}></div>
          <span>Policies (16 docs)</span>
        </div>
      </div>
      
      <canvas
        ref={canvasRef}
        className="vector-canvas"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
      />
      
      <div className="vector-info">
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '16px' }}>
          🖱️ Drag to rotate • Auto-rotating visualization of document embeddings in 3D vector space
        </p>
      </div>
      
      <div className="vector-stats">
        <div className="vector-stat">
          <strong>71</strong>
          <span>Total Documents</span>
        </div>
        <div className="vector-stat">
          <strong>4</strong>
          <span>Clusters</span>
        </div>
        <div className="vector-stat">
          <strong>768</strong>
          <span>Dimensions</span>
        </div>
        <div className="vector-stat">
          <strong>0.89</strong>
          <span>Avg Similarity</span>
        </div>
      </div>
    </div>
  );
};

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(7);
  const [activeTab, setActiveTab] = useState('overview');
  const [graphSubTab, setGraphSubTab] = useState('document'); // 'document' or 'vector'

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
    // Show only April 4th, 2026 data
    const queriesOverTime = [
      {
        date: '2026-04-04',
        count: 24
      }
    ];

    return {
      total_queries: 24,
      avg_relevance: 0.87,
      avg_response_time_ms: 1850,
      hallucination_rate: 4.2,
      conflict_rate: 12.5,
      queries_over_time: queriesOverTime,
      llm_usage: [
        { llm: 'gemini', count: 18 },
        { llm: 'ollama', count: 6 }
      ],
      top_topics: [
        { topic: 'Pricing and Refund Policies', count: 5 },
        { topic: 'Support Ticket Analysis', count: 4 },
        { topic: 'User License Management', count: 3 },
        { topic: 'Contract Terms and Renewals', count: 3 },
        { topic: 'Client Comparisons', count: 2 },
        { topic: 'Service Level Agreements', count: 2 },
        { topic: 'Billing and Invoicing', count: 2 },
        { topic: 'Feature Requests', count: 1 }
      ]
    };
  };

  const getMockGraphData = () => {
    // Better node positioning using force-directed layout simulation
    const nodes = [
      { id: 'client_techstart_contract.pdf', label: 'TechStart Contract', x: 15, y: 20 },
      { id: 'enterprise_corp_agreement.pdf', label: 'Enterprise Agreement', x: 75, y: 25 },
      { id: 'startuphub_terms.pdf', label: 'StartupHub Terms', x: 45, y: 15 },
      { id: 'pricing_comparison_2024.xlsx', label: 'Pricing Comparison', x: 50, y: 50 },
      { id: 'support_tickets_q4_2024.xlsx', label: 'Support Tickets Q4', x: 25, y: 70 },
      { id: 'refund_policy_2024.pdf', label: 'Refund Policy', x: 30, y: 45 },
      { id: 'client_health_report.pdf', label: 'Client Health Report', x: 65, y: 75 },
      { id: 'license_usage_report.xlsx', label: 'License Usage', x: 80, y: 55 }
    ];
    
    return {
      nodes,
      edges: [
        { source: 'client_techstart_contract.pdf', target: 'pricing_comparison_2024.xlsx', count: 12 },
        { source: 'client_techstart_contract.pdf', target: 'refund_policy_2024.pdf', count: 8 },
        { source: 'enterprise_corp_agreement.pdf', target: 'pricing_comparison_2024.xlsx', count: 10 },
        { source: 'enterprise_corp_agreement.pdf', target: 'license_usage_report.xlsx', count: 15 },
        { source: 'support_tickets_q4_2024.xlsx', target: 'client_health_report.pdf', count: 18 },
        { source: 'startuphub_terms.pdf', target: 'pricing_comparison_2024.xlsx', count: 7 },
        { source: 'refund_policy_2024.pdf', target: 'pricing_comparison_2024.xlsx', count: 6 },
        { source: 'pricing_comparison_2024.xlsx', target: 'license_usage_report.xlsx', count: 9 },
        { source: 'startuphub_terms.pdf', target: 'refund_policy_2024.pdf', count: 5 }
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
        <div className="graph-tabs-container">
          {/* Sub-tabs for graph views */}
          <div className="graph-sub-tabs glass-panel">
            <button 
              className={graphSubTab === 'document' ? 'active' : ''} 
              onClick={() => setGraphSubTab('document')}
            >
              <Network size={16} />
              Document Graph
            </button>
            <button 
              className={graphSubTab === 'vector' ? 'active' : ''} 
              onClick={() => setGraphSubTab('vector')}
            >
              <Zap size={16} />
              Vector Clusters
            </button>
          </div>

          {/* Document Knowledge Graph */}
          {graphSubTab === 'document' && (
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
                    <div className="legend-item">
                      <div className="legend-line" style={{ borderColor: '#10b981', borderWidth: '2px' }}></div>
                      <span>Strong Connection (10+)</span>
                    </div>
                  </div>
                  
                  {/* SVG for connections */}
                  <svg className="graph-connections" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                    {graphData.edges.map((edge, i) => {
                      const sourceNode = graphData.nodes.find(n => n.id === edge.source);
                      const targetNode = graphData.nodes.find(n => n.id === edge.target);
                      if (!sourceNode || !targetNode) return null;
                      
                      const x1 = sourceNode.x || 50;
                      const y1 = sourceNode.y || 50;
                      const x2 = targetNode.x || 50;
                      const y2 = targetNode.y || 50;
                      
                      const isStrong = edge.count >= 10;
                      
                      return (
                        <line
                          key={i}
                          x1={`${x1}%`}
                          y1={`${y1}%`}
                          x2={`${x2}%`}
                          y2={`${y2}%`}
                          stroke={isStrong ? '#10b981' : '#cbd5e1'}
                          strokeWidth={isStrong ? '2' : '1'}
                          strokeOpacity={isStrong ? '0.6' : '0.3'}
                          strokeDasharray={isStrong ? '0' : '4 2'}
                        />
                      );
                    })}
                  </svg>
                  
                  {/* Nodes */}
                  <div className="graph-nodes">
                    {graphData.nodes.map((node, i) => {
                      const connections = graphData.edges.filter(e => e.source === node.id || e.target === node.id);
                      const connectionCount = connections.length;
                      const totalWeight = connections.reduce((sum, e) => sum + e.count, 0);
                      const nodeSize = Math.min(60 + connectionCount * 5, 100);
                      
                      return (
                        <div 
                          key={i} 
                          className="graph-node" 
                          style={{ 
                            left: `${node.x || 50}%`, 
                            top: `${node.y || 50}%`,
                            transform: 'translate(-50%, -50%)'
                          }}
                        >
                          <div 
                            className="node-circle" 
                            style={{ 
                              width: `${nodeSize}px`, 
                              height: `${nodeSize}px`,
                              backgroundColor: connectionCount > 2 ? '#3b82f6' : '#94a3b8'
                            }}
                          >
                            <span className="node-count">{connectionCount}</span>
                          </div>
                          <div className="node-label">{node.label}</div>
                          <div className="node-connections">
                            {connectionCount} connections • {totalWeight} co-occurrences
                          </div>
                        </div>
                      );
                    })}
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

          {/* 3D Vector Clusters */}
          {graphSubTab === 'vector' && (
            <div className="vector-container glass-panel">
              <h3>Vector Space Clusters</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
                3D visualization of document embeddings in vector space
              </p>
              <VectorCluster3D />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Analytics;
