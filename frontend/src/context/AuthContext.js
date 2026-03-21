import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = (email, password) => {
    // Mock login
    const mockUser = {
      email,
      name: email.split('@')[0],
      id: '1'
    };
    setUser(mockUser);
    localStorage.setItem('user', JSON.stringify(mockUser));
    return Promise.resolve(mockUser);
  };

  const signup = (email, password) => {
    // Mock signup - returns verification needed
    return Promise.resolve({ needsVerification: true, email });
  };

  const verifyEmail = (code) => {
    // Mock verification
    if (code.length === 6) {
      const mockUser = {
        email: 'user@example.com',
        name: 'Usuario',
        id: '1'
      };
      setUser(mockUser);
      localStorage.setItem('user', JSON.stringify(mockUser));
      return Promise.resolve(mockUser);
    }
    return Promise.reject(new Error('Invalid code'));
  };

  const loginWithGoogle = () => {
    // Mock Google login
    const mockUser = {
      email: 'google@example.com',
      name: 'Google User',
      id: '1'
    };
    setUser(mockUser);
    localStorage.setItem('user', JSON.stringify(mockUser));
    return Promise.resolve(mockUser);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    loading,
    login,
    signup,
    verifyEmail,
    loginWithGoogle,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
