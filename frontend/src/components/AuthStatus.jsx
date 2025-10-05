import React, { useState, useEffect } from 'react';
import apiClient from '../api';

const AuthStatus = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiClient.get('/api/users/me');
        setUser(response.data);
      } catch (error) {
        if (error.response && error.response.status !== 401) {
          console.error("Failed to fetch user status:", error);
        }
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="auth-status">
      {user ? (
        <span>Welcome, {user.email}</span>
      ) : (
        <a href="/api/auth/google/authorize">Connect Calendar</a>
      )}
    </div>
  );
};

export default AuthStatus;