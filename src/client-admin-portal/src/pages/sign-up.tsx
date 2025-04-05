'use client';
import NonNavbarLogo from '@/components/NonNavbarLogo';
import SignUpForm from '@/components/SignUpForm';
import { Container } from '@mui/material';
import React from 'react';

const SignUpPage = () => {
  return (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        py: 6,
      }}
    >
      <NonNavbarLogo />
      <SignUpForm />
    </Container>
  );
};

export default SignUpPage;
