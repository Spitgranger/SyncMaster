import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  IconButton,
  InputAdornment,
  Box,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { resetPassword } from '@/services/authService';

interface ResetPasswordFormProps {
  email: string;
}

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({ email }) => {
  const [password, setPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    const IdToken = localStorage.getItem('IdToken');
    if (!IdToken) {
      console.error('User ID not found in localStorage!');
      return;
    }

    try {
      await resetPassword(email, password, newPassword, IdToken);
      window.location.href = '/acknowledgement'; // Redirect after success
    } catch (err) {
      setError('Failed to reset password. Please try again.');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, px: 2 }}>
      <Typography
        variant="h5"
        fontWeight="bold"
        textAlign="center"
        gutterBottom
      >
        Reset Password
      </Typography>
      <Typography
        variant="body1"
        color="text.secondary"
        textAlign="center"
        gutterBottom
      >
        Enter your current one-time password and set a new password.
      </Typography>

      {error && (
        <Typography color="error" textAlign="center">
          {error}
        </Typography>
      )}

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
        <TextField
          fullWidth
          label="One-Time Password"
          variant="filled"
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          sx={{ mb: 3, backgroundColor: '#f5f5f5' }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <TextField
          fullWidth
          label="New Password"
          variant="filled"
          type={showNewPassword ? 'text' : 'password'}
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          sx={{ mb: 4, backgroundColor: '#f5f5f5' }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <VisibilityOff /> : <Visibility />}
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
          RESET PASSWORD
        </Button>
      </Box>
    </Container>
  );
};

export default ResetPasswordForm;
