"use client";
import React, { useState, useEffect } from 'react';
import { Container, TextField, Button, Typography, MenuItem, Select, FormControl, InputLabel, Box, CircularProgress } from '@mui/material';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { createUser, resetCreateUserStatus } from '@/state/user/userManagementSlice'; // Import the reset action
import { RootState, AppDispatch } from '@/state/store';

const AddUserForm: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();
  const { idToken } = useSelector((state: RootState) => state.user);
  const { createUserStatus, error } = useSelector((state: RootState) => state.userManagement);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  // Reset createUserStatus on component mount so the form starts fresh
  useEffect(() => {
    dispatch(resetCreateUserStatus());
  }, [dispatch]);

  // Redirect after a successful user creation
  useEffect(() => {
    if (createUserStatus === 'succeeded') {
      // Reset status before redirecting to avoid instant redirect on subsequent visits
      dispatch(resetCreateUserStatus());
      setTimeout(() => router.push('/dashboard/manageusers'), 2000);
    }
  }, [createUserStatus, router, dispatch]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLocalError(null);

    if (!name || !email || !company || !role) {
      setLocalError('All fields are required');
      return;
    }

    if (!idToken) {
      setLocalError('Authentication token not found. Please sign in again.');
      return;
    }

    // Dispatch the createUser thunk with the necessary data
    dispatch(createUser({
      email,
      attributes: {
        "custom:role": role as 'admin' | 'contractor' | 'employee',
        "custom:company": company,
        name,
      }
    }));
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" textAlign="center" gutterBottom>
        Add New User
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" gutterBottom>
        Please enter the following details about the new user
      </Typography>

      {localError && <Typography color="error" textAlign="center">{localError}</Typography>}
      {error && <Typography color="error" textAlign="center">{error}</Typography>}
      {createUserStatus === 'succeeded' && (
        <Typography color="success.main" textAlign="center">
          User created successfully! Redirecting...
        </Typography>
      )}

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
        <TextField
          fullWidth
          label="Name"
          variant="outlined"
          value={name}
          onChange={(e) => setName(e.target.value)}
          sx={{ mb: 3 }}
        />
        <TextField
          fullWidth
          label="Email"
          variant="outlined"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{ mb: 3 }}
        />
        <TextField
          fullWidth
          label="Company Name"
          variant="outlined"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          sx={{ mb: 3 }}
        />
        <FormControl fullWidth sx={{ mb: 4 }}>
          <InputLabel>User Role</InputLabel>
          <Select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            label="User Role"
          >
            <MenuItem value="admin">Admin</MenuItem>
            <MenuItem value="employee">Employee</MenuItem>
            <MenuItem value="contractor">Contractor</MenuItem>
          </Select>
        </FormControl>
        <Button type="submit" variant="contained" color="primary" fullWidth disabled={createUserStatus === 'loading'}>
          {createUserStatus === 'loading' ? <CircularProgress size={24} /> : '+ ADD NEW USER'}
        </Button>
      </Box>
    </Container>
  );
};

export default AddUserForm;
