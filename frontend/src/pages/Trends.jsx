import Sidebar from '../components/Sidebar.jsx';

const TRENDING_ROLES = [
  { role: 'AI / ML Engineer',        change: '+41%', demand: 92, salary: '€65,000–90,000', skills: ['Python', 'PyTorch', 'TensorFlow', 'AWS'] },
  { role: 'Cybersecurity Analyst',   change: '+38%', demand: 87, salary: '€55,000–78,000', skills: ['Linux', 'Network Security', 'Python'] },
  { role: 'Data Engineer',           change: '+34%', demand: 85, salary: '€60,000–85,000', skills: ['Python', 'SQL', 'Apache Spark', 'AWS'] },
  { role: 'Full Stack Developer',    change: '+22%', demand: 78, salary: '€52,000–75,000', skills: ['React', 'Node.js', 'TypeScript', 'Docker'] },
  { role: 'Data Analyst',            change: '+19%', demand: 75, salary: '€45,000–62,000', skills: ['SQL', 'Python', 'Tableau', 'Excel'] },
  { role: 'Product Manager',         change: '+17%', demand: 70, salary: '€58,000–80,000', skills: ['Agile', 'Scrum', 'Jira', 'Communication'] },
  { role: 'UX / Product Designer',   change: '+15%', demand: 65, salary: '€48,000–68,000', skills: ['Figma', 'UI/UX', 'User Research'] },
  { role: 'Business Analyst',        change: '+13%', demand: 62, salary: '€48,000–65,000', skills: ['Excel', 'SQL', 'Tableau', 'SAP'] },
  { role: 'Cloud / DevOps Engineer', change: '+12%', demand: 60, salary: '€62,000–88,000', skills: ['Docker', 'Kubernetes', 'AWS', 'Terraform'] },
  { role: 'SAP Consultant',          change: '+10%', demand: 55, salary: '€55,000–80,000', skills: ['SAP', 'ERP', 'Finance'] },
];

const IN_DEMAND_SKILLS = [
  { name: 'Python',          heat: 95 },
  { name: 'SQL',             heat: 88 },
  { name: 'Machine Learning',heat: 82 },
  { name: 'React',           heat: 78 },
  { name: 'Docker',          heat: 75 },
  { name: 'AWS',             heat: 73 },
  { name: 'TypeScript',      heat: 70 },
  { name: 'Tableau',         heat: 65 },
  { name: 'SAP',             heat: 62 },
  { name: 'Excel',           heat: 60 },
];

const MARKET_INSIGHTS = [
  { icon: '🏢', stat: '12,400+', label: 'Tech jobs in Berlin' },
  { icon: '💶', stat: '€62,000', label: 'Avg. tech salary (Berlin)' },
  { icon: '📈', stat: '+28%',    label: 'YoY job growth (2024→2025)' },
  { icon: '🌍', stat: '68%',     label: 'Jobs open to international students' },
];

export default function Trends() {
  return (
    <div className="app">
      <Sidebar />
      <div className="main">
        <div>
          <h1 className="page-title">📈 Market Trends · Berlin</h1>

          {/* Market stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
            {MARKET_INSIGHTS.map(m => (
              <div key={m.label} className="card" style={{ textAlign: 'center', marginBottom: 0 }}>
                <div style={{ fontSize: 28, marginBottom: 4 }}>{m.icon}</div>
                <div style={{ fontSize: 22, fontWeight: 800, color: '#1a2238' }}>{m.stat}</div>
                <div style={{ fontSize: 11, color: '#6b7494', marginTop: 4 }}>{m.label}</div>
              </div>
            ))}
          </div>

          {/* Trending roles */}
          <div className="card">
            <h2 className="section-title">🔥 Fastest-Growing Roles in Germany</h2>
            <p style={{ fontSize: 13, color: '#6b7494', marginTop: 0 }}>
              Year-over-year job posting growth on German job boards.
            </p>
            {TRENDING_ROLES.map((r, i) => (
              <div key={r.role} style={{
                display: 'flex', alignItems: 'center', gap: 14,
                padding: '12px 0', borderBottom: i < TRENDING_ROLES.length - 1 ? '1px solid #f0f2f8' : 'none',
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 8,
                  background: '#f0f2f8', color: '#1a2238',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 700, fontSize: 12, flexShrink: 0,
                }}>{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{r.role}</div>
                  <div style={{ fontSize: 11, color: '#6b7494', marginTop: 3 }}>
                    {r.salary} · Skills: {r.skills.join(', ')}
                  </div>
                  <div style={{ marginTop: 6, background: '#f0f2f8', borderRadius: 4, height: 4, overflow: 'hidden' }}>
                    <div style={{ width: `${r.demand}%`, height: '100%', background: '#c9f04d' }} />
                  </div>
                </div>
                <div style={{ color: '#2a9d8f', fontWeight: 700, fontSize: 15, flexShrink: 0 }}>↑ {r.change}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right col */}
        <div className="right-col">
          <div className="card">
            <h2 className="section-title">⚡ Most In-Demand Skills</h2>
            <p style={{ fontSize: 12, color: '#6b7494', marginTop: 0 }}>
              Based on Berlin job postings.
            </p>
            {IN_DEMAND_SKILLS.map(s => (
              <div key={s.name} style={{ marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                  <span style={{ fontWeight: 500 }}>{s.name}</span>
                  <span style={{ color: '#6b7494', fontSize: 11 }}>{s.heat}% of jobs</span>
                </div>
                <div className="bar">
                  <span style={{ width: `${s.heat}%`, background: s.heat >= 80 ? '#c9f04d' : '#a8d8a8' }} />
                </div>
              </div>
            ))}
          </div>

          <div className="card">
            <h2 className="section-title">🎓 GISMA Programmes in Demand</h2>
            {[
              { course: 'Data Science & Analytics', match: '94%' },
              { course: 'Computer Science',          match: '91%' },
              { course: 'Digital Business',          match: '85%' },
              { course: 'Business Administration',   match: '78%' },
              { course: 'Marketing Management',      match: '72%' },
            ].map(p => (
              <div key={p.course} className="label-row">
                <span style={{ fontSize: 13 }}>{p.course}</span>
                <span style={{ color: '#2a9d8f', fontWeight: 600, fontSize: 13 }}>{p.match}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
