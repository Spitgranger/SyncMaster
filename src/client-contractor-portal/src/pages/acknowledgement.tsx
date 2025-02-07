'use client';

import React from 'react';
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/router";
import { useEffect } from "react";
import { Container } from '@mui/material';
import AcknowledgmentForm from '@/components/AcknowledgementForm';
import NonNavbarLogo from '@/components/NonNavbarLogo';

const AcknowledgementPage = () => {

  const isAuthenticated = useAuth();
  const router = useRouter();

  const fakeDocuments = [
    { name: 'HSE Document', url: 'https://web.hamilton/entry-exit-protocols' },
    { name: 'Fire Protocol Document', url: 'https://web.hamilton/entry-exit-protocols' },
  ];

  const handleProceed = () => {
    console.log('Acknowledged and proceeding...');
  };
  
  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/"); // Redirect to login if not authenticated
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated === null) return <p>Loading...</p>;

  

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
      <AcknowledgmentForm documents={fakeDocuments} onProceed={handleProceed} />
    </Container>
  );
};

export default AcknowledgementPage;
