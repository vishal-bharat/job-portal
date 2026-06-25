import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, setSession, getUser } from '../api/client.js';

export default function Login() {
  const nav = useNavigate();
  if (getUser()) { nav('/', { replace: true }); }

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await api.login(email, password);
      nav('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <div className="brand-logo" style={{ marginBottom: 16 }}>G</div>
        <h1>Career Connect</h1>
        <p>Sign in to find opportunities matched to your skills.</p>

        {error && <div className="error">{error}</div>}

        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />

        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />

        <button className="btn-primary" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>

        <div className="hint" style={{ marginTop: 6 }}>
          New student? <a href="/signup" style={{ color: '#1a2238', fontWeight: 600 }}>Create account →</a>
        </div>
      </form>
    </div>
  );
}
