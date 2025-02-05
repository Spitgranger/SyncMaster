'use clinet'
import React from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { Container } from '@mui/material'
import Grid from '@mui/material/Grid2';

export default function SiteWideDocuments() {
  return (
    <Container maxWidth={"lg"}>
      <Grid container>
        <Grid size={12} sx={{
          width: "100%"
        }}>
          Content
        </Grid>
      </Grid>
    </Container>
  )
}



SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>
}