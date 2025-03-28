"use client"
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress
} from '@mui/material';
import { getSiteVisits } from '@/state/site/siteVisitsSlice';
import { RootState, AppDispatch } from '@/state/store';

const SiteVisitsTable: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { idToken } = useSelector((state: RootState) => state.user);
  const { visits, isLoading } = useSelector((state: RootState) => state.siteVisits);

  useEffect(() => {
    if (!idToken) {
      console.error('Authentication token not found. Please sign in.');
      return;
    }
    dispatch(getSiteVisits({ params: {}, idToken }));
  }, [dispatch, idToken]);

  return (
    <>
      <Container sx={{ mt: 0, px: 0 }}>
        <Typography variant="h5" fontWeight="bold" textAlign="left" gutterBottom>
          Site Visits
        </Typography>
      </Container>
      <Container sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 6 }}>
        {isLoading ? (
          <CircularProgress />
        ) : (
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
                {visits && visits.length > 0 ? (
                  visits.map((visit, index) => (
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
        )}
      </Container>
    </>
  );
};

export default SiteVisitsTable;
