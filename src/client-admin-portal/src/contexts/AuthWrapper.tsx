'use client';

import { isAuthenticated } from '@/utils/userHelpers';
import { useRouter } from 'next/router';
import React, { useState, useEffect } from 'react';

interface AuthProviderProps {
  children: React.ReactNode;
}

const AuthProvider = ({ children }: AuthProviderProps) => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if the user is authenticated
    const checkAuth = () => {
      const isAuth = isAuthenticated();
      console.log('isAuth', isAuth);

      const pathname = window.location.pathname;

      // If the user is trying to access the dashboard and is not authenticated, redirect to login
      if (pathname.includes('/dashboard') && !isAuth) {
        router.push('/login');
      } else {
        // If authenticated or not on /dashboard, allow the page to load
        setLoading(false);
      }
    };

    // Run the authentication check on mount
    checkAuth();
  }, [router]);

  if (loading) {
    return <div>Loading...</div>; // Show loading state while checking authentication
  }

  return <>{children}</>;
};

export default AuthProvider;
