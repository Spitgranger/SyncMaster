'use client';
import React, { useState } from 'react';
import Grid from '@mui/material/Grid2';
import {
  Button,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import CircularProgress from '@mui/material/CircularProgress';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useDispatch } from 'react-redux';
import { signInUser } from '@/state/user/userSlice';
import { AppDispatch } from '@/state/store';

const SignInForm = () => {
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [emailError, setEmailError] = useState(false);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSignInButtonDisabled, setIsSignInButtonDisabled] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  const handleEmailClickAway = (e: React.FocusEvent<HTMLInputElement>) => {
    if (e.target.validity.valid) {
      setEmailError(false);
    } else {
      setEmailError(true);
    }
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
  };

  const handleClickShowPassword = () => setShowPassword((prev) => !prev);
  const handleMouseDownPassword = (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    event.preventDefault();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSignInButtonDisabled(true);
    setErrorMessage(''); // Clear any previous error message
    try {
      // Using unwrap() will throw an error if the thunk is rejected
      const response = await dispatch(signInUser({ email, password })).unwrap();
      localStorage.setItem('accessToken', response.AccessToken);
      localStorage.setItem('idToken', response.IdToken);
      router.push('/dashboard/sitewide');
    } catch (error: any) {
      if (error.message.includes('OTP detected')) {
        console.log('OTP detected; redirecting to reset-password page.');
      } else {
        console.error('Sign in error:', error.message);
        // 2. Set the errorMessage state based on the error
        setErrorMessage(
          error.message || 'Something went wrong during sign in.'
        );
      }
    } finally {
      setIsSignInButtonDisabled(false);
    }
  };

  return (
    <Grid
      container
      boxShadow={16}
      direction={'column'}
      sx={{
        width: '100%',
        maxWidth: '552px',
        px: '24px',
      }}
    >
      <form onSubmit={handleSubmit}>
        <Grid size={12} py={2}>
          <Typography variant="h5">Sign In</Typography>
        </Grid>
        {errorMessage && (
          <Grid size={12} py={1}>
            <Typography color="error">{errorMessage}</Typography>
          </Grid>
        )}
        <Grid size={12} container direction={'column'} spacing={2} py={2}>
          <TextField
            type="email"
            required
            error={emailError}
            name="email"
            value={email}
            onChange={handleEmailChange}
            onBlur={handleEmailClickAway}
            fullWidth
            variant="outlined"
            placeholder="Email"
            helperText={emailError && 'Please enter a valid email address'}
          />

          <TextField
            type={showPassword ? 'text' : 'password'}
            required
            name="password"
            value={password}
            onChange={handlePasswordChange}
            fullWidth
            variant="outlined"
            placeholder="Password"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    aria-label={
                      showPassword
                        ? 'hide the password'
                        : 'display the password'
                    }
                    onClick={handleClickShowPassword}
                    onMouseDown={handleMouseDownPassword}
                  >
                    {showPassword ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Button
            disabled={isSignInButtonDisabled}
            type="submit"
            size="large"
            variant="contained"
            style={{ minWidth: '100px', minHeight: '36px' }}
          >
            {isSignInButtonDisabled ? (
              <CircularProgress size={24} />
            ) : (
              'Sign In'
            )}
          </Button>

          <Grid display={'flex'} justifyContent={'center'}>
            <Link
              style={{ textAlign: 'center', color: '#1976d2' }}
              href={'/sign-up'}
            >
              <Typography variant="body1">Request Account</Typography>
            </Link>
          </Grid>

          <Grid display={'flex'} justifyContent={'center'}>
            <Link
              style={{ textAlign: 'right', color: '#1976d2' }}
              href={'/reset-password'}
            >
              <Typography variant="body1">Reset Password</Typography>
            </Link>
          </Grid>
        </Grid>
      </form>
    </Grid>
  );
};

export default SignInForm;
