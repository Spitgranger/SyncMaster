'use client';
import React from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Container } from '@mui/material';
import SiteVisitsTable from '@/components/SiteVisitsComponent';

export default function SiteWideDocuments() {
  return (
    <Container maxWidth={false}>
      <SiteVisitsTable />
    </Container>
  );
}

SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>;
};
