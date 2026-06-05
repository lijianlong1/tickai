import React, { createContext, useContext, useState, useEffect } from 'react';
import { getUser, clearUser, authApi, saveUser } from '../services/api';

const UserContext = createContext(null);

export function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 从本地存储加载用户信息
    const loadUser = () => {
      const storedUser = getUser();
      console.log('从 localStorage 加载的用户:', storedUser);
      if (storedUser) {
        const userWithDetails = {
          ...storedUser,
          account: storedUser.email.split('@')[0],
          avatar: storedUser.avatar || '👨‍🎨'
        };
        setUser(userWithDetails);
      } else {
        setUser(null);
      }
      setLoading(false);
    };
    
    loadUser();
  }, []);

  const login = async (credentials) => {
    const response = await authApi.login(credentials);
    const userData = response.data;
    const userWithDetails = {
      ...userData,
      account: userData.email.split('@')[0],
      avatar: '👨‍🎨'
    };
    saveUser(userData, userData.token);
    setUser(userWithDetails);
    return response;
  };

  const register = async (userData) => {
    const response = await authApi.register(userData);
    const userDataFromApi = response.data;
    const userWithDetails = {
      ...userDataFromApi,
      account: userDataFromApi.email.split('@')[0],
      avatar: '👨‍🎨'
    };
    saveUser(userDataFromApi, userDataFromApi.token);
    setUser(userWithDetails);
    return response;
  };

  const logout = () => {
    clearUser();
    setUser(null);
  };

  return (
    <UserContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
