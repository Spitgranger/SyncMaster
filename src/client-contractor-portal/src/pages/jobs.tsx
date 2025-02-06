// pages/jobs.js
'use client';

import React from 'react';
import { Container, Box } from '@mui/material';
import TopNavBar from '@/components/TopNavBar';
import EndVisit from '@/components/EndVisit';
import BottomNavBar from '@/components/BottomNavBar';

const JobsPage = () => {
  const handleEndVisit = () => {
    console.log('EndVisit Clicked');
  };

  return (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        padding: 0,
      }}
    >
      {/* Top Navigation Bar */}
      <TopNavBar />

      {/* Main Content */}
      <Box
        sx={{
          flexGrow: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <EndVisit onEndVisit={handleEndVisit} />
      </Box>

      {/* Bottom Navigation Bar */}
      <BottomNavBar />
    </Container>
  );
};

export default JobsPage;
