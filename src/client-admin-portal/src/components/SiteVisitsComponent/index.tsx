import React, { useState, useEffect } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { getSiteVisits } from '@/services/getSiteVisits';

interface SiteVisit {
  site_id: string;
  user_id: string;
  entry_time: string;
  exit_time?: string;
}

const SiteVisitsTable: React.FC = () => {
  const [siteVisits, setSiteVisits] = useState<SiteVisit[]>([]);

  useEffect(() => {
    const fetchSiteVisits = async () => {
      try {
        const idToken = localStorage.getItem('IdToken');
        if (!idToken) {
          console.error('Authentication token not found. Please sign in.');
          return;
        }
        const visits = await getSiteVisits({ user_role: "admin" }, idToken);
        setSiteVisits(visits);
      } catch (error) {
        console.error("Failed to fetch site visits", error);
      }
    };

    fetchSiteVisits();
  }, []);

  return (
    <Container sx={{ mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" textAlign="left" gutterBottom>
        Site Visits
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Site ID</strong></TableCell>
              <TableCell><strong>User ID</strong></TableCell>
              <TableCell><strong>Entry Time</strong></TableCell>
              <TableCell><strong>Exit Time</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {siteVisits.length > 0 ? (
              siteVisits.map((visit, index) => (
                <TableRow key={index}>
                  <TableCell>{visit.site_id}</TableCell>
                  <TableCell>{visit.user_id}</TableCell>
                  <TableCell>{new Date(visit.entry_time).toLocaleString()}</TableCell>
                  <TableCell>{visit.exit_time ? new Date(visit.exit_time).toLocaleString() : 'N/A'}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={4} align="center">No site visits found</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default SiteVisitsTable;
