'use client';

import React from 'react';
import { Container } from '@mui/material';
import SignInForm from '@/components/SignInForm';
import NonNavbarLogo from '@/components/NonNavbarLogo';

const LoginPage = () => {
  return (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        py: 4,
      }}
    >
      <NonNavbarLogo />
      <SignInForm />
    </Container>
  );
};

export default LoginPage;
