"use client";

import { isAuthenticated } from '@/utils/userHelpers';
import { useRouter } from 'next/router';
import React, { useState, useEffect } from 'react';
import CircularProgress from '@mui/material/CircularProgress';

interface AuthProviderProps {
  children: React.ReactNode;
}

const AuthProvider = ({ children }: AuthProviderProps) => {
  const router = useRouter();
  const { id } = router.query;
  
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if the user is authenticated
    const checkAuth = () => {
      const isAuth = isAuthenticated();
      console.log("isAuth", isAuth);
      
      const pathname = window.location.pathname;

      // If the user is trying to access the portal and is not authenticated, redirect to login
      if (pathname.includes("/portal") && !isAuth) {
        router.push("/login");
      } else {
        // If authenticated or not on /portal, allow the page to load
        setLoading(false);
      }
    };

    // Run the authentication check on mount
    checkAuth();
  }, [router]);

  if (loading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <CircularProgress />
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthProvider;
