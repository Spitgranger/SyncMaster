'use client';

import React from 'react';
import { Container } from '@mui/material';
import TopNavBar from '@/components/TopNavBar';
import BottomNavBar from '@/components/BottomNavBar';
import DocumentList from '@/components/DocumentList';

const DocumentsPage = () => {
  {/* Fake Data */}
  const fetchDocuments = async () => {
    return [
      {
        name: 'Project Plans',
        files: [
          { name: 'Blueprint.pdf' },
          { name: 'Project Timeline.xlsx' }
        ]
      },
      {
        name: 'Safety Procedures',
        files: [
          { name: 'Emergency Response.pdf' },
          { name: 'Fire Safety Guidelines.docx' }
        ]
      },
      {
        name: 'Environmental Policies',
        files: [
          { name: 'Waste Management.pdf' },
          { name: 'Sustainability Plan.docx' }
        ]
      },
      {
        name: 'General Documents',
        files: [
          { name: 'Employee Handbook.pdf' },
          { name: 'Inspection Reports.xlsx' },
          { name: 'Maintenance Log.docx' }
        ]
      }
    ];
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
      <DocumentList fetchDocuments={fetchDocuments} />

      {/* Bottom Navigation Bar */}
      <BottomNavBar />
    </Container>
  );
};

export default DocumentsPage;
