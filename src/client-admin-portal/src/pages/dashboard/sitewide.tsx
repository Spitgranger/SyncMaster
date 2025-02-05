import DashboardLayout from '@/components/layouts/DashboardLayout'
import React from 'react'

export default function SiteWideDocuments() {
  return (
    <div>sitewideDocuments</div>
  )
}



SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement){
  return <DashboardLayout>{page}</DashboardLayout>
}