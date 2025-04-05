'use client';
import React from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Container } from '@mui/material';
import UserRequests from '@/components/userRequests';

export default function SiteWideDocuments() {
  return (
    <Container maxWidth={'lg'}>
      <UserRequests />
    </Container>
  );
}

SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>;
};
