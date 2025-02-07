'use clinet'
import React from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { Container } from '@mui/material'
import ManageUsersTable from '@/components/ManageUsers'

export default function SiteWideDocuments() {
  return (
    <Container maxWidth={"lg"}>
      <ManageUsersTable />
    </Container>
  )
}



SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>
}