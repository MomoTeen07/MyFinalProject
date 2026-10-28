import { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const expireSession = () => setUser(null);
    const syncSession = (event) => {
      if (event.key === 'token' && !event.newValue) setUser(null);
    };
    window.addEventListener('auth:expired', expireSession);
    window.addEventListener('storage', syncSession);
    if (!localStorage.getItem('token')) {
      setLoading(false);
      return () => {
        window.removeEventListener('auth:expired', expireSession);
        window.removeEventListener('storage', syncSession);
      };
    }
    let active = true;
    api('/api/users/me')
      .then((currentUser) => { if (active) setUser(currentUser); })
      .catch(() => { if (active) localStorage.removeItem('token'); })
      .finally(() => { if (active) setLoading(false); });
    return () => {
      active = false;
      window.removeEventListener('auth:expired', expireSession);
      window.removeEventListener('storage', syncSession);
    };
  }, []);

  const authenticate = async (path, payload) => {
    const result = await api(path, { method: 'POST', body: JSON.stringify(payload) });
    localStorage.setItem('token', result.access_token);
    try {
      const currentUser = await api('/api/users/me');
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      localStorage.removeItem('token');
      throw error;
    }
  };

  const value = {
    user,
    loading,
    login: (email, password) => authenticate('/api/auth/login', { email, password }),
    register: (name, email, password) => authenticate('/api/auth/register', { name, email, password }),
    logout: () => { localStorage.removeItem('token'); setUser(null); },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used inside AuthProvider');
  return context;
}
