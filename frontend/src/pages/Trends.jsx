import { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar.jsx';
import Loader  from '../components/Loader.jsx';
import { api } from '../api/client.js';

export default function Trends() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState('');

  useEffect(() => {
    api.trends()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="app"><Sidebar />
      <div className="main" style={{ gridTemplateColumns: '1fr' }}>
        <Loader fullPage text="Fetching live Berlin job market data…" />
      </div>
    </div>
  );

  const topSkills = data?.top_skills || [];
  const topRoles  = data?.top_roles  || [];
  const total     = data?.total_jobs_fetched || 0;
  const updated   = data?.last_updated || '';

  // For the bar charts we need a maximum count to normalise widths
  const maxSkillCount = topSkills.reduce((m, s) => Math.max(m, s.count), 1);
  const maxRoleCount  = topRoles.reduce( (m, r) => Math.max(m, r.count), 1);

  return (
    <div className="app">
      <Sidebar />
      <div className="main">
        <div>
          <h1 className="page-title">📈 Market Trends · Berlin</h1>

          {error && (
            <div className="error">
              Could not load live market data: {error}. Please try again in a moment.
            </div>
          )}

          {/* Live data summary row */}
          {!error && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 20 }}>
              <div className="card" style={{ textAlign: 'center', marginBottom: 0 }}>
                <div style={{ fontSize: 28, marginBottom: 4 }}>📋</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#1a2238' }}>{total}</div>
                <div style={{ fontSize: 11, color: '#6b7494', marginTop: 4 }}>Live jobs sampled</div>
              </div>
              <div className="card" style={{ textAlign: 'center', marginBottom: 0 }}>
                <div style={{ fontSize: 28, marginBottom: 4 }}>🔧</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#1a2238' }}>{topSkills.length}</div>
                <div style={{ fontSize: 11, color: '#6b7494', marginTop: 4 }}>Distinct skills tracked</div>
              </div>
              <div className="card" style={{ textAlign: 'center', marginBottom: 0 }}>
                <div style={{ fontSize: 28, marginBottom: 4 }}>💼</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#1a2238' }}>{topRoles.length}</div>
                <div style={{ fontSize: 11, color: '#6b7494', marginTop: 4 }}>Role categories found</div>
              </div>
            </div>
          )}

          {/* Trending roles */}
          <div className="card">
            <h2 className="section-title">🔥 Most In-Demand Roles in Berlin</h2>
            <p style={{ fontSize: 13, color: '#6b7494', marginTop: 0 }}>
              Ranked by number of active job postings on Bundesagentur für Arbeit.
              {updated && (
                <span style={{ marginLeft: 8, color: '#9ca3af', fontSize: 11 }}>
                  Updated {updated}
                </span>
              )}
            </p>

            {topRoles.length === 0 && !error && (
              <div style={{ color: '#6b7494', fontSize: 13 }}>
                No role data available right now — the Bundesagentur API may be temporarily unavailable.
              </div>
            )}

            {topRoles.map((r, i) => (
              <div key={r.role} style={{
                display: 'flex', alignItems: 'center', gap: 14,
                padding: '12px 0',
                borderBottom: i < topRoles.length - 1 ? '1px solid #f0f2f8' : 'none',
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 8,
                  background: '#f0f2f8', color: '#1a2238',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 12, flexShrink: 0,
                }}>{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{r.role}</div>
                  <div style={{ marginTop: 6, background: '#f0f2f8', borderRadius: 4, height: 4, overflow: 'hidden' }}>
                    <div style={{
                      width: `${Math.round((r.count / maxRoleCount) * 100)}%`,
                      height: '100%', background: '#c9f04d',
                    }} />
                  </div>
                </div>
                <div style={{ color: '#2a9d8f', fontWeight: 700, fontSize: 14, flexShrink: 0, minWidth: 60, textAlign: 'right' }}>
                  {r.count} job{r.count !== 1 ? 's' : ''}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right col */}
        <div className="right-col">
          <div className="card">
            <h2 className="section-title">⚡ Most In-Demand Skills</h2>
            <p style={{ fontSize: 12, color: '#6b7494', marginTop: 0 }}>
              Extracted from live Berlin job descriptions (Bundesagentur).
            </p>

            {topSkills.length === 0 && !error && (
              <div style={{ color: '#6b7494', fontSize: 13 }}>
                No skill data available right now.
              </div>
            )}

            {topSkills.map(s => (
              <div key={s.name} style={{ marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                  <span style={{ fontWeight: 500 }}>{s.name}</span>
                  <span style={{ color: '#6b7494', fontSize: 11 }}>
                    {s.count} job{s.count !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="bar">
                  <span style={{
                    width: `${Math.round((s.count / maxSkillCount) * 100)}%`,
                    background: s.count / maxSkillCount >= 0.7 ? '#c9f04d' : '#a8d8a8',
                  }} />
                </div>
              </div>
            ))}
          </div>

          <div className="card">
            <h2 className="section-title">ℹ️ Data Source</h2>
            <p style={{ fontSize: 13, color: '#6b7494', lineHeight: 1.6, marginBottom: 0 }}>
              This page queries the <strong>Bundesagentur für Arbeit</strong> (Germany's Federal
              Employment Agency) in real time across 8 job categories. Skills are extracted
              from live job descriptions using our keyword extraction engine. Data is refreshed
              every hour.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
