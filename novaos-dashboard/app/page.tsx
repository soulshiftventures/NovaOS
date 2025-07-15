'use client';
import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [queueDepth, setQueueDepth] = useState(0);
  const [socketStatus, setSocketStatus] = useState('disconnected');

  useEffect(() => {
    async function fetchMetrics() {
      try {
        const res = await fetch('/api/metrics');
        const data = await res.json();
        setQueueDepth(data.queueDepth || 0);
        setSocketStatus(data.socketStatus || 'disconnected');
      } catch {
        setSocketStatus('error');
      }
    }
    fetchMetrics();
    const id = setInterval(fetchMetrics, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ padding: '2rem', background: '#111', color: '#fff', minHeight: '100vh' }}>
      <h1 style={{ fontSize: '2.5rem', color: '#3b82f6' }}>NovaOS Dashboard</h1>
      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
        <div style={{ flex: 1, background: '#1f2937', padding: '1rem', borderRadius: '0.5rem' }}>
          <h2 style={{ color: '#10b981' }}>Queue Depth</h2>
          <p style={{ fontSize: '2rem' }}>{queueDepth}</p>
        </div>
        <div style={{ flex: 1, background: '#1f2937', padding: '1rem', borderRadius: '0.5rem' }}>
          <h2 style={{ color: '#3b82f6' }}>Socket Status</h2>
          <p style={{ fontSize: '2rem' }}>{socketStatus}</p>
        </div>
      </div>
    </div>
  );
}
