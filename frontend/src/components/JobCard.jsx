import { useState } from 'react';

const ICONS = {
  'Siemens': '⚙️',
  'HelloFresh': '🥗',
  'Delivery Hero': '🛵',
  'Zalando': '👗',
  'BMW Group': '🚗',
  'N26': '🏦',
  'Trivago': '🏨',
  'SAP': '☁️',
  'Booking.com': '🌍',
  'Spotify': '🎧',
  'About You': '👕',
  'Flink': '⚡'
};

// Source badge — only shown for real API jobs, not for seed/LinkedIn-search fallbacks
const SOURCE_BADGE = {
  arbeitsagentur: { label: 'Arbeitsagentur', bg: '#005b96', color: '#fff' },
  adzuna:         { label: 'Germany Jobs',   bg: '#2563eb', color: '#fff' },
  linkedin:       { label: 'LinkedIn',       bg: '#0a66c2', color: '#fff' },
};

// Apply button colour per source (seed jobs get a neutral dark)
const APPLY_STYLE = {
  arbeitsagentur: { bg: '#005b96', color: '#fff' },
  adzuna:         { bg: '#2563eb', color: '#fff' },
  linkedin:       { bg: '#0a66c2', color: '#fff' },
  seed:           { bg: '#1a2238', color: '#fff' },
};

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const days = Math.round((Date.now() - d.getTime()) / 86400000);
  if (days <= 0) return 'today';
  if (days === 1) return '1 day ago';
  return `${days} days ago`;
}

export default function JobCard({ job, savedIds = [], onSave }) {
  const matchClass  = job.matchPercent >= 50 ? '' : 'match-low';
  const missing     = job.missingSkills || [];
  const srcBadge    = SOURCE_BADGE[job.source];           // undefined for seed — no badge
  const applyStyle  = APPLY_STYLE[job.source] || APPLY_STYLE.seed;
  const hasApply    = !!job.applyUrl;                      // any job with a URL gets the button
  const isSaved     = savedIds.includes(String(job.id));
  const [saving, setSaving] = useState(false);

  return (
    <div className="job">
      <div className="job-icon">{ICONS[job.company] || '💼'}</div>

      <div className="job-body">
        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <div className="job-title">{job.title}</div>

          {/* Source badge — only for real API jobs */}
          {srcBadge && (
            <span style={{
              fontSize: 10, fontWeight: 700, padding: '2px 7px',
              background: srcBadge.bg, color: srcBadge.color,
              borderRadius: 99, whiteSpace: 'nowrap', letterSpacing: '0.02em',
            }}>
              {srcBadge.label}
            </span>
          )}

          {/* BERT semantic boost badge */}
          {job.semanticBoost && (
            <span style={{
              fontSize: 10, fontWeight: 600, padding: '2px 6px',
              background: '#e0f2fe', color: '#0369a1',
              borderRadius: 99, whiteSpace: 'nowrap',
            }}>
              BERT match
            </span>
          )}
        </div>

        <div className="job-company">{job.company} · {job.location}</div>

        {/* Required skills — yellow highlight if missing */}
        <div className="job-tags">
          {job.requiredSkills.map((s) => {
            const isMissing = missing.includes(s);
            return (
              <span
                key={s}
                className="job-tag"
                style={isMissing ? { background: '#fef3c7', color: '#92400e', border: '1px solid #fcd34d' } : {}}
                title={isMissing ? `You don't have ${s} yet` : `You have ${s}`}
              >
                {isMissing ? '⚠ ' : ''}{s}
              </span>
            );
          })}
        </div>

        {/* Skill gap hint */}
        {missing.length > 0 && (
          <div style={{ fontSize: 11, color: '#92400e', marginTop: 4 }}>
            Skill gap: learn <strong>{missing.slice(0, 3).join(', ')}</strong>
            {missing.length > 3 ? ` + ${missing.length - 3} more` : ''} to strengthen this match
          </div>
        )}

        {/* Meta row */}
        <div className="job-meta">
          {job.salary && <span>💰 {job.salary}</span>}
          <span>🕒 {timeAgo(job.postedDate)}</span>
          <span>📌 {job.jobType}</span>
        </div>
      </div>

      {/* Right column: match pill + save + apply */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8, flexShrink: 0 }}>
        <div className={`match-pill ${matchClass}`}>{job.matchPercent}% match</div>

        {/* Save button */}
        {onSave && (
          <button
            disabled={saving || isSaved}
            onClick={async () => {
              setSaving(true);
              await onSave(job);
              setSaving(false);
            }}
            style={{
              padding: '6px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
              border: '1px solid #e1e5ee',
              background: isSaved ? '#f0f2f8' : '#fff',
              color: isSaved ? '#6b7494' : '#1a2238',
              cursor: isSaved ? 'default' : 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            {isSaved ? '✓ Saved' : saving ? '…' : '🔖 Save'}
          </button>
        )}

        {/* Apply button — every job has a URL (real link or LinkedIn search fallback) */}
        {hasApply && (
          <a
            href={job.applyUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-block', padding: '6px 14px',
              background: applyStyle.bg, color: applyStyle.color,
              borderRadius: 8, fontSize: 12, fontWeight: 600,
              textDecoration: 'none', whiteSpace: 'nowrap',
            }}
          >
            Apply →
          </a>
        )}
      </div>
    </div>
  );
}
