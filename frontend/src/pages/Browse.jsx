import { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar.jsx';
import JobCard from '../components/JobCard.jsx';
import Loader  from '../components/Loader.jsx';
import { api } from '../api/client.js';

const QUICK_SEARCHES = [
  'Python Developer', 'Data Analyst', 'Business Analyst',
  'React Developer', 'Machine Learning', 'UX Designer',
  'Java Developer', 'Marketing Manager', 'Project Manager',
];

function normaliseJob(job) {
  return {
    ...job,
    matchPercent:   job.match_percent   ?? job.matchPercent   ?? 0,
    requiredSkills: job.required_skills ?? job.requiredSkills ?? [],
    missingSkills:  job.missing_skills  ?? job.missingSkills  ?? [],
    semanticBoost:  job.semantic_boost  ?? job.semanticBoost  ?? false,
    postedDate:     job.posted_date     ?? job.postedDate,
    jobType:        job.job_type        ?? job.jobType,
    applyUrl:       job.apply_url       ?? job.applyUrl       ?? null,
    source:         job.source          ?? 'seed',
  };
}

export default function Browse() {
  const [query, setQuery]     = useState('');
  const [results, setResults] = useState([]);
  const [savedIds, setSavedIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError]     = useState('');

  useEffect(() => {
    api.listApplications().then(apps => setSavedIds(apps.map(a => String(a.external_job_id)))).catch(() => {});
  }, []);

  const doSearch = async (q = query) => {
    if (!q.trim()) return;
    setLoading(true); setError(''); setSearched(true);
    try {
      const jobs = await api.searchJobs(q.trim());
      setResults(jobs.map(normaliseJob));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleSaveJob = async (job) => {
    try {
      await api.saveApplication({
        external_job_id: String(job.id),
        title: job.title,
        company: job.company,
        location: job.location,
        job_type: job.jobType,
        salary: job.salary,
        apply_url: job.applyUrl,
        source: job.source,
      });
      setSavedIds(prev => [...new Set([...prev, String(job.id)])]);
    } catch (e) { setError(e.message); }
  };

  return (
    <div className="app">
      <Sidebar />
      <div className="main" style={{ gridTemplateColumns: '1fr' }}>
        <div>
          <h1 className="page-title">Browse Jobs · Berlin</h1>

          {/* Search bar */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', gap: 10 }}>
              <input
                style={{
                  flex: 1, padding: '12px 16px', borderRadius: 10,
                  border: '1px solid #e1e5ee', fontSize: 14, outline: 'none',
                }}
                placeholder="e.g. Python Developer, Business Analyst, UX Designer…"
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && doSearch()}
              />
              <button className="btn-primary" onClick={() => doSearch()} disabled={loading}>
                {loading ? 'Searching…' : '🔎 Search'}
              </button>
            </div>

            {/* Quick search chips */}
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 11, color: '#6b7494', letterSpacing: 1, marginBottom: 8, textTransform: 'uppercase' }}>
                Quick searches
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {QUICK_SEARCHES.map(q => (
                  <span
                    key={q}
                    className="chip chip-suggested"
                    onClick={() => { setQuery(q); doSearch(q); }}
                    style={{ cursor: 'pointer' }}
                  >
                    {q}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {error && <div className="error">{error}</div>}

          {/* Results */}
          {loading && <Loader text="Fetching live jobs from Berlin…" />}

          {!loading && searched && results.length === 0 && (
            <div className="card" style={{ textAlign: 'center', padding: '40px 20px', color: '#6b7494' }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>🔍</div>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>No results found</div>
              <div style={{ fontSize: 13 }}>Try a broader keyword like "Developer" or "Analyst".</div>
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                <h2 className="section-title" style={{ margin: 0 }}>
                  Results for "{query}"
                </h2>
                <span style={{ fontSize: 12, color: '#6b7494' }}>{results.length} jobs</span>
              </div>
              {results.map(j => (
                <JobCard key={j.id} job={j} savedIds={savedIds} onSave={handleSaveJob} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
