import React, { useState } from 'react';
import { Container, Typography, TextField, Button, IconButton, InputAdornment, Box } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';

const EmailPasswordForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log('Email:', email);
    console.log('Password:', password);
  };

  const handleClickShowPassword = () => setShowPassword((show) => !show);
  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, px: 2 }}> {/* 16px margin on sides */}
      {/* Header */}
      <Typography variant="h5" fontWeight="bold" textAlign="center" gutterBottom>
        Identification Information
      </Typography>

      {/* Instruction Text */}
      <Typography variant="body1" color="text.secondary" textAlign="center" gutterBottom>
        Please enter your email and password below
      </Typography>

      {/* Form */}
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
        <TextField
          fullWidth
          label="Email"
          variant="filled"
          type="email"
          value={email}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
          sx={{ mb: 3, backgroundColor: '#f5f5f5' }}
        />

        <TextField
          fullWidth
          label="Password"
          variant="filled"
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
          sx={{ mb: 4, backgroundColor: '#f5f5f5' }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  onClick={handleClickShowPassword}
                  onMouseDown={handleMouseDownPassword}
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          sx={{ py: 1.5 }}
        >
          CONTINUE
        </Button>
      </Box>
    </Container>
  );
};

export default EmailPasswordForm;