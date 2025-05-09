'use client';
import React from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Container } from '@mui/material';
import AddUserForm from '@/components/AddUserForm';

export default function SiteWideDocuments() {
  return (
    <Container maxWidth={'lg'}>
      <AddUserForm />
    </Container>
  );
}

SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>;
};
