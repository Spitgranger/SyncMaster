'use client';

import React from 'react';
import { useRouter } from 'next/router';
import { Container } from '@mui/material';
import ResetPasswordForm from '@/components/ResetPasswordForm';
import NonNavbarLogo from '@/components/NonNavbarLogo';

const ResetPasswordPage = () => {
  const router = useRouter();
  const { email } = router.query; // ✅ Extract email from query parameters

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
      {email ? (
        <ResetPasswordForm email={email as string} />
      ) : (
        <p>Loading...</p>
      )}
    </Container>
  );
};

export default ResetPasswordPage;
