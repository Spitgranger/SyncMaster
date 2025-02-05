// pages/jobs.js
'use client';

import React from 'react';
import { Container, Box } from '@mui/material';
import TopNavBar from '@/components/TopNavBar';
import AddJob from '@/components/AddJob';
import BottomNavBar from '@/components/BottomNavBar';

const JobsPage = () => {
  const handleAddJob = () => {
    console.log('Add New Job Clicked');
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
        <AddJob onAddJob={handleAddJob} />
      </Box>

      {/* Bottom Navigation Bar */}
      <BottomNavBar />
    </Container>
  );
};

export default JobsPage;
