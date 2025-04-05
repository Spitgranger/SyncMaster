'use client';
import React, { useState } from 'react';
import Grid from '@mui/material/Grid2';
import {
  Button,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
  Alert,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import CircularProgress from '@mui/material/CircularProgress';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { signInUser } from '@/state/user/userSlice';
import { AppDispatch } from '@/state/store';

const ResetPasswordForm = () => {
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordMismatchError, setPasswordMismatchError] = useState(false);
  const [isSubmitDisabled, setIsSubmitDisabled] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  const handleEmailBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.target.validity.valid) {
      setEmailError(false);
    } else {
      setEmailError(true);
    }
  };

  const handleOldPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOldPassword(e.target.value);
  };

  const handleNewPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewPassword(e.target.value);
  };

  const handleConfirmNewPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setConfirmNewPassword(e.target.value);
  };

  const toggleShowOldPassword = () => setShowOldPassword((prev) => !prev);
  const toggleShowNewPassword = () => setShowNewPassword((prev) => !prev);
  const toggleShowConfirmPassword = () =>
    setShowConfirmPassword((prev) => !prev);

  const handleMouseDownPassword = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setPasswordMismatchError(false);

    // Validate new password confirmation
    if (newPassword !== confirmNewPassword) {
      setPasswordMismatchError(true);
      return;
    }

    setIsSubmitDisabled(true);
    try {
      // Dispatch signInUser with the optional new_password field
      const response = await dispatch(
        signInUser({
          email,
          password: oldPassword,
          new_password: newPassword,
        })
      ).unwrap();

      // Store tokens as needed
      localStorage.setItem('accessToken', response.AccessToken);
      localStorage.setItem('idToken', response.IdToken);

      // Display success message and navigate to the next page
      setSuccessMessage('Password successfully set');
      setTimeout(() => {
        router.push('/dashboard/sitewide');
      }, 1000);
    } catch (error: any) {
      console.error('Reset password error:', error.message);
      setErrorMessage(error.message || 'Something went wrong during sign in.');
    } finally {
      setIsSubmitDisabled(false);
    }
  };

  return (
    <Grid
      container
      boxShadow={16}
      direction="column"
      sx={{ width: '100%', maxWidth: '552px', px: '24px' }}
    >
      <form onSubmit={handleSubmit}>
        <Grid py={2}>
          <Typography variant="h5">Reset Password</Typography>
        </Grid>
        {successMessage && (
          <Grid py={2}>
            <Alert severity="success">{successMessage}</Alert>
          </Grid>
        )}
        {errorMessage && (
          <Grid size={12} py={1}>
            <Typography color="error">{errorMessage}</Typography>
          </Grid>
        )}
        <Grid container direction="column" spacing={2} py={2}>
          <Grid>
            <TextField
              type="email"
              required
              error={emailError}
              name="email"
              value={email}
              onChange={handleEmailChange}
              onBlur={handleEmailBlur}
              fullWidth
              variant="outlined"
              placeholder="Email"
              helperText={emailError && 'Please enter a valid email address'}
            />
          </Grid>
          <Grid>
            <TextField
              type={showOldPassword ? 'text' : 'password'}
              required
              name="oldPassword"
              value={oldPassword}
              onChange={handleOldPasswordChange}
              fullWidth
              variant="outlined"
              placeholder="Old Password"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={
                        showOldPassword
                          ? 'hide old password'
                          : 'show old password'
                      }
                      onClick={toggleShowOldPassword}
                      onMouseDown={handleMouseDownPassword}
                    >
                      {showOldPassword ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid>
            <TextField
              type={showNewPassword ? 'text' : 'password'}
              required
              name="newPassword"
              value={newPassword}
              onChange={handleNewPasswordChange}
              fullWidth
              variant="outlined"
              placeholder="New Password"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={
                        showNewPassword
                          ? 'hide new password'
                          : 'show new password'
                      }
                      onClick={toggleShowNewPassword}
                      onMouseDown={handleMouseDownPassword}
                    >
                      {showNewPassword ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid>
            <TextField
              type={showConfirmPassword ? 'text' : 'password'}
              required
              name="confirmNewPassword"
              value={confirmNewPassword}
              onChange={handleConfirmNewPasswordChange}
              fullWidth
              variant="outlined"
              placeholder="Confirm New Password"
              error={passwordMismatchError}
              helperText={passwordMismatchError && 'Passwords do not match'}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label={
                        showConfirmPassword
                          ? 'hide confirm password'
                          : 'show confirm password'
                      }
                      onClick={toggleShowConfirmPassword}
                      onMouseDown={handleMouseDownPassword}
                    >
                      {showConfirmPassword ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid display="flex" justifyContent="center">
            <Button
              disabled={isSubmitDisabled}
              type="submit"
              size="large"
              variant="contained"
            >
              {isSubmitDisabled ? (
                <CircularProgress size={24} />
              ) : (
                'Reset Password'
              )}
            </Button>
          </Grid>
          <Grid display="flex" justifyContent="center">
            <Link
              href="/login"
              style={{ textAlign: 'center', color: '#1976d2' }}
            >
              <Typography variant="body1">Back to Sign In</Typography>
            </Link>
          </Grid>
        </Grid>
      </form>
    </Grid>
  );
};

export default ResetPasswordForm;
