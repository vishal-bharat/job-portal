import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, setSession } from '../api/client.js';

const COURSES = [
  'Computer Science',
  'Data Science & Analytics',
  'Business Administration',
  'International Management',
  'Marketing Management',
  'Finance & Accounting',
  'Digital Business',
  'Project Management',
  'Human Resource Management',
];

export default function Signup() {
  const nav = useNavigate();
  const [form, setForm] = useState({
    name: '', email: '', password: '',
    university: 'GISMA University of Applied Sciences',
    course: '', year: '',
  });
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return; }
    setLoading(true);
    try {
      const res = await api.signup({
        ...form,
        year: form.year ? Number(form.year) : null,
      });
      setSession(res.token, { email: res.email, name: res.name, course: form.course });
      nav('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit} style={{ width: 420 }}>
        <div className="brand-logo" style={{ marginBottom: 16 }}>G</div>
        <h1>Create account</h1>
        <p>Join GISMA Career Connect and get personalised job matches.</p>

        {error && <div className="error">{error}</div>}

        <label>Full name</label>
        <input value={form.name} onChange={set('name')} required placeholder="Alex Schmidt" />

        <label>Email</label>
        <input value={form.email} onChange={set('email')} type="email" required placeholder="you@gisma.edu" />

        <label>Password</label>
        <input value={form.password} onChange={set('password')} type="password" required placeholder="Min. 6 characters" />

        <label>University</label>
        <input value={form.university} onChange={set('university')} placeholder="GISMA University…" />

        <label>Course</label>
        <select
          value={form.course}
          onChange={set('course')}
          style={{
            width: '100%', padding: '12px 14px',
            borderRadius: 10, border: '1px solid #e1e5ee',
            fontSize: 14, outline: 'none', marginBottom: 14,
            background: '#fff', color: form.course ? '#1a2238' : '#9ca3af',
          }}
        >
          <option value="">Select your course</option>
          {COURSES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        <label>Year of study</label>
        <input value={form.year} onChange={set('year')} type="number" min="1" max="6" placeholder="e.g. 1" />

        <button className="btn-primary" disabled={loading} style={{ marginTop: 4 }}>
          {loading ? 'Creating account…' : 'Create account'}
        </button>

        <div className="hint">
          Already have an account? <Link to="/login" style={{ color: '#1a2238', fontWeight: 600 }}>Sign in</Link>
        </div>
      </form>
    </div>
  );
}
