'use client';

import React from 'react';
import { Container, Box, Typography, TextField } from '@mui/material';
import TopNavBar from '@/components/TopNavBar';
import EndVisit from '@/components/EndVisit';
import BottomNavBar from '@/components/BottomNavBar';
import PortalLayout from '@/components/layouts/PortalLayout';
import WorkIcon from '@mui/icons-material/Work';
import EditIcon from '@mui/icons-material/Edit';
import { Construction } from '@mui/icons-material';


export default function JobsPage() {
  const handleEndVisit = () => {
    console.log('EndVisit Clicked');
  };

  return (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: 3,
      }}
    >
      <Typography variant="h5" fontWeight={"bold"} sx={{ mb: 2 }}>
        Visit Details
      </Typography>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%',
        }}
      >
        <Box sx={{ display: "flex", width: "100%", justifyContent: "space-between", mb: 2, p: 1, alignItems: "center" }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }} >
            <WorkIcon />
            <Typography ml={1} variant='body1'>Work Order Number</Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }} >
            <TextField sx={{ mr: 1, "& .MuiInputBase-input": { fontSize: 12, height: 5, padding: 1, width: "60px" } }} value={"HXZU892"} ></TextField>
            <EditIcon />
          </Box>

          {/* <Typography variant='body1'>123456</Typography> */}
        </Box>

        <Box sx={{ display: "flex", flexDirection: 'column', width: "100%", mb: 2, p: 1, }}>
          <Box sx={{ display: "flex", width: "100%", justifyContent: "space-between", mb: 1, alignItems: "center" }}>
            <Typography variant='h6'>
              Comments
            </Typography>
            <EditIcon />
          </Box>
          <TextField
            multiline
            rows={4}
            variant="outlined"
            placeholder="Enter comments here"
          />

        </Box>

        <Box sx={{ display: "flex", flexDirection: 'column', width: "100%", mb: 1, p: 1, }}>

            <Typography variant='h6' sx={{ mb: 2 }}>
              Files
            </Typography>
            <Typography variant='body1' color='black' sx={{ mb: 1 }}>
              Uploaded Files
            </Typography>

        </Box>
        

      </Box>

      <EndVisit onEndVisit={handleEndVisit} />

    </Container>
  );
};

JobsPage.getLayout = function getLayout(page: React.ReactElement) {
  return <PortalLayout>{page}</PortalLayout>
}