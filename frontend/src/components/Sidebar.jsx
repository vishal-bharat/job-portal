import { useNavigate, useLocation } from 'react-router-dom';
import { getUser, clearSession } from '../api/client.js';

const NAV = [
  { label: 'Opportunities', path: '/',             icon: '🎯', section: 'STUDENT' },
  { label: 'My Profile',    path: '/profile',      icon: '👤', section: 'STUDENT' },
  { label: 'Applications',  path: '/applications', icon: '📋', section: 'STUDENT' },
  { label: 'Browse Jobs',   path: '/browse',       icon: '🔎', section: 'EXPLORE' },
  { label: 'Market Trends', path: '/trends',       icon: '📈', section: 'EXPLORE' },
  { label: 'Skill Gap',     path: '/skill-gap',    icon: '🧩', section: 'TOOLS' },
];

export default function Sidebar() {
  const nav  = useNavigate();
  const loc  = useLocation();
  const user = getUser();

  const handleLogout = () => {
    clearSession();
    nav('/login');
  };

  let lastSection = null;
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-logo">G</div>
        <div className="brand-name">GISMA</div>
        <div className="brand-sub">University of Applied Sciences</div>
        <div className="brand-tag">CAREER CONNECT</div>
      </div>

      {NAV.map((item) => {
        const showLabel = item.section !== lastSection;
        lastSection = item.section;
        return (
          <div key={item.path}>
            {showLabel && <div className="section-label">{item.section}</div>}
            <div
              className={`nav-item ${loc.pathname === item.path ? 'active' : ''}`}
              onClick={() => nav(item.path)}
            >
              <span>{item.icon}</span> {item.label}
            </div>
          </div>
        );
      })}

      <div className="sidebar-footer">
        <div className="avatar">
          {(user?.name || 'S').split(' ').map(p => p[0]).join('').slice(0, 2)}
        </div>
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <div className="user-name" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {user?.name || 'Student'}
          </div>
          <div className="user-meta" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {user?.course || 'GISMA'}
          </div>
        </div>
        <button className="btn-link" onClick={handleLogout} title="Log out">↪</button>
      </div>
    </aside>
  );
}
