import { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar.jsx';
import { api } from '../api/client.js';

const STATUS_CONFIG = {
  saved:        { label: 'Saved',        color: '#6b7494', bg: '#f0f2f8' },
  applied:      { label: 'Applied',      color: '#0369a1', bg: '#e0f2fe' },
  interviewing: { label: 'Interviewing', color: '#7c3aed', bg: '#ede9fe' },
  offered:      { label: 'Offered',      color: '#15803d', bg: '#dcfce7' },
  rejected:     { label: 'Rejected',     color: '#b91c1c', bg: '#fee2e2' },
};

const SOURCE_COLOR = {
  arbeitsagentur: '#005b96',
  stepstone: '#ff6600',
  linkedin: '#0a66c2',
  seed: '#6b7494',
};

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.saved;
  return (
    <span style={{
      fontSize: 11, fontWeight: 700, padding: '3px 10px',
      background: cfg.bg, color: cfg.color, borderRadius: 99,
    }}>
      {cfg.label}
    </span>
  );
}

function ApplicationCard({ app, onStatusChange, onDelete }) {
  const [changing, setChanging] = useState(false);

  const handleStatus = async (newStatus) => {
    setChanging(true);
    await onStatusChange(app.id, newStatus);
    setChanging(false);
  };

  return (
    <div style={{
      border: '1px solid #eceff7', borderRadius: 14,
      padding: '16px 18px', marginBottom: 12, background: '#fff',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
            <span style={{ fontWeight: 700, fontSize: 15 }}>{app.title}</span>
            <StatusBadge status={app.status} />
            {app.source && app.source !== 'seed' && (
              <span style={{
                fontSize: 10, fontWeight: 700, padding: '2px 7px',
                background: SOURCE_COLOR[app.source] || '#6b7494',
                color: '#fff', borderRadius: 99,
              }}>
                {app.source === 'arbeitsagentur' ? 'Arbeitsagentur' : app.source === 'stepstone' ? 'StepStone' : 'LinkedIn'}
              </span>
            )}
          </div>
          <div style={{ color: '#6b7494', fontSize: 13 }}>
            {app.company} {app.location ? `· ${app.location}` : ''} {app.job_type ? `· ${app.job_type}` : ''}
          </div>
          {app.salary && <div style={{ fontSize: 12, color: '#2a9d8f', marginTop: 4 }}>💰 {app.salary}</div>}
          <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 6 }}>
            Saved {new Date(app.saved_at).toLocaleDateString('en-DE', { day: 'numeric', month: 'short', year: 'numeric' })}
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end', flexShrink: 0, marginLeft: 12 }}>
          {app.apply_url && (
            <a
              href={app.apply_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                background: SOURCE_COLOR[app.source] || '#1a2238',
                color: '#fff', textDecoration: 'none',
              }}
            >
              Apply →
            </a>
          )}
          <button
            onClick={() => onDelete(app.id)}
            style={{ background: 'none', border: 'none', color: '#9ca3af', fontSize: 12, cursor: 'pointer', padding: 0 }}
          >
            Remove
          </button>
        </div>
      </div>

      {/* Status stepper */}
      <div style={{ marginTop: 14, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
          <button
            key={key}
            disabled={changing || app.status === key}
            onClick={() => handleStatus(key)}
            style={{
              padding: '5px 12px', borderRadius: 99, fontSize: 11, fontWeight: 600,
              border: `1px solid ${app.status === key ? cfg.color : '#e1e5ee'}`,
              background: app.status === key ? cfg.bg : '#fff',
              color: app.status === key ? cfg.color : '#6b7494',
              cursor: app.status === key ? 'default' : 'pointer',
              opacity: changing ? 0.6 : 1,
            }}
          >
            {cfg.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export default function Applications() {
  const [apps, setApps]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');

  const load = async () => {
    try {
      const data = await api.listApplications();
      setApps(data);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleStatusChange = async (id, status) => {
    try {
      const updated = await api.updateApplicationStatus(id, status);
      setApps(apps.map(a => a.id === id ? updated : a));
    } catch (e) { setError(e.message); }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteApplication(id);
      setApps(apps.filter(a => a.id !== id));
    } catch (e) { setError(e.message); }
  };

  // Group by status
  const counts = Object.fromEntries(
    Object.keys(STATUS_CONFIG).map(s => [s, apps.filter(a => a.status === s).length])
  );

  return (
    <div className="app">
      <Sidebar />
      <div className="main" style={{ gridTemplateColumns: '1fr' }}>
        <div>
          <h1 className="page-title">My Applications</h1>
          {error && <div className="error">{error}</div>}

          {/* Summary row */}
          <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
            {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
              <div key={key} style={{
                padding: '10px 18px', borderRadius: 12, background: '#fff',
                border: '1px solid #eceff7', textAlign: 'center', minWidth: 90,
              }}>
                <div style={{ fontSize: 22, fontWeight: 700, color: cfg.color }}>{counts[key] || 0}</div>
                <div style={{ fontSize: 11, color: '#6b7494', marginTop: 2 }}>{cfg.label}</div>
              </div>
            ))}
          </div>

          {loading && <p style={{ color: '#6b7494' }}>Loading…</p>}

          {!loading && apps.length === 0 && (
            <div className="card" style={{ textAlign: 'center', padding: '40px 20px', color: '#6b7494' }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>📋</div>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>No saved jobs yet</div>
              <div style={{ fontSize: 13 }}>
                Go to <a href="/" style={{ color: '#1a2238', fontWeight: 600 }}>Opportunities</a> and click <strong>Save</strong> on any job to track it here.
              </div>
            </div>
          )}

          {apps.map(app => (
            <ApplicationCard
              key={app.id}
              app={app}
              onStatusChange={handleStatusChange}
              onDelete={handleDelete}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
