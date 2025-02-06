'use client';

import React from 'react';
import { Container } from '@mui/material';
import AcknowledgmentForm from '@/components/AcknowledgementForm';
import NonNavbarLogo from '@/components/NonNavbarLogo';

const AcknowledgementPage = () => {
  const fakeDocuments = [
    { name: 'HSE Document', url: 'https://web.hamilton/entry-exit-protocols' },
    { name: 'Fire Protocol Document', url: 'https://web.hamilton/entry-exit-protocols' },
  ];

  const handleProceed = () => {
    console.log('Acknowledged and proceeding...');
  };

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
