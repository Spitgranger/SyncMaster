'use client'
import React from 'react';
import Container from '@mui/material/Container';
import { Box, Typography } from '@mui/material';
import NonNavbarLogo from '@/components/NonNavbarLogo'

const EndVisitPage = () => {
  return (
    <Container maxWidth="sm" sx={{ display: 'flex', alignItems: 'center', minHeight: '100vh' }}>
      <Box
        sx={{
          width: '100%',
          p: 3,
          boxShadow: 16,
          textAlign: 'center',
          borderRadius: 2,
          mx: 'auto'
        }}
      >
        <NonNavbarLogo />
        <Typography variant="h5" gutterBottom>
          Thank You for Working with Hamilton Water
        </Typography>
        <Typography variant="body1">
          You have been logged out and may now close this tab.
        </Typography>
      </Box>
    </Container>
  );
};

export default EndVisitPage;
