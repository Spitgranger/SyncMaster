import React, { useState, useEffect } from 'react';
import { Container, TextField, Button, Typography, MenuItem, Select, FormControl, InputLabel, Box } from '@mui/material';
import { createUser } from '@/services/userService';
import { useRouter } from 'next/router';

const AddUserForm: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [idToken, setIdToken] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    // Since this is a client component, localStorage is available.
    const token = localStorage.getItem('idToken');
    setIdToken(token);
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!name || !email || !company || !role) {
      setError('All fields are required');
      return;
    }

    if (!idToken) {
      setError('Authentication token not found. Please sign in again.');
      return;
    }

    try {
      // Pass the IdToken as required by the API
      await createUser(email, role as 'admin' | 'contractor' | 'employee', company, name, idToken);
      setSuccess(true);
      setTimeout(() => router.push('/dashboard/manageusers'), 2000); // Redirect after success
    } catch (err: any) {
      setError('Failed to create user. Please try again.');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" textAlign="center" gutterBottom>
        Add New User
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" gutterBottom>
        Please enter the following details about the new user
      </Typography>

      {error && <Typography color="error" textAlign="center">{error}</Typography>}
      {success && (
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
        <Button type="submit" variant="contained" color="primary" fullWidth>
          + ADD NEW USER
        </Button>
      </Box>
    </Container>
  );
};

export default AddUserForm;
