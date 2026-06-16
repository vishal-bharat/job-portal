import { Routes, Route, Navigate } from 'react-router-dom';
import Login        from './pages/Login.jsx';
import Signup       from './pages/Signup.jsx';
import Dashboard    from './pages/Dashboard.jsx';
import Profile      from './pages/Profile.jsx';
import Applications from './pages/Applications.jsx';
import Browse       from './pages/Browse.jsx';
import Trends       from './pages/Trends.jsx';
import SkillGap     from './pages/SkillGap.jsx';
import { getUser }  from './api/client.js';

function RequireAuth({ children }) {
  const user = getUser();
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login"  element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route path="/"            element={<RequireAuth><Dashboard /></RequireAuth>} />
      <Route path="/profile"     element={<RequireAuth><Profile /></RequireAuth>} />
      <Route path="/applications"element={<RequireAuth><Applications /></RequireAuth>} />
      <Route path="/browse"      element={<RequireAuth><Browse /></RequireAuth>} />
      <Route path="/trends"      element={<RequireAuth><Trends /></RequireAuth>} />
      <Route path="/skill-gap"   element={<RequireAuth><SkillGap /></RequireAuth>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
