import React, { useEffect, useState } from 'react';
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
  Button,
  CircularProgress
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { getUserRequests, actionRequest } from '@/state/user/userRequestsSlice';
import { AppDispatch, RootState } from '@/state/store';

const UserRequests: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { requests, loading, error } = useSelector((state: RootState) => state.userRequests);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    // Fetch the user requests on component mount.
    dispatch(getUserRequests({}));
  }, [dispatch]);

  const handleAction = async (email: string, action: 'approve' | 'reject') => {
    try {
      await dispatch(actionRequest({ email, action })).unwrap();
      if (action === 'approve') {
        setSuccessMsg(`User ${email} was successfully added`);
        // Clear the message after 3 seconds.
        setTimeout(() => setSuccessMsg(null), 3000);
      }
      // Refresh the list after performing the action.
      dispatch(getUserRequests({}));
    } catch (err) {
      console.error("Failed to perform action on user request", err);
    }
  };

  return (
    <Container sx={{ mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        User Requests
      </Typography>
      {successMsg && (
        <Typography color="success.main" textAlign="center">
          {successMsg}
        </Typography>
      )}
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Name</strong></TableCell>
                <TableCell><strong>Email</strong></TableCell>
                <TableCell><strong>Company</strong></TableCell>
                <TableCell><strong>Role Requested</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests && requests.length > 0 ? (
                requests.map((request, index) => (
                  <TableRow key={index}>
                    <TableCell>{request.name}</TableCell>
                    <TableCell>{request.email}</TableCell>
                    <TableCell>{request.company}</TableCell>
                    <TableCell>{request.role_requested}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        onClick={() => handleAction(request.email, 'approve')}
                        sx={{ mr: 1 }}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="outlined"
                        color="secondary"
                        size="small"
                        onClick={() => handleAction(request.email, 'reject')}
                      >
                        Reject
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No user requests found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default UserRequests;
