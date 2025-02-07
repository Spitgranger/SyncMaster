'use clinet'
import React from 'react'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { Container } from '@mui/material'
import DocumentTreeComponent from '@/components/DocumentTreeComponent'
import processPath from '@/utils/test2'

export default function SiteWideDocuments() {
  return (
    <Container maxWidth={"lg"}>
      <DocumentTreeComponent />
    </Container>
  )
}



SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>
}