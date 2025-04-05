import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  IconButton,
  InputAdornment,
  Box,
  CircularProgress,
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useRouter } from 'next/router';
import { AppDispatch } from '@/state/store';
import { useDispatch } from 'react-redux';
import { setSiteId, signInUser } from '@/state/user/userSlice';
import getGeolocation from '@/utils/getLocation';

const SignInForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { id } = router.query;

  const dispatch = useDispatch<AppDispatch>();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const location = await getGeolocation();
    if (
      location.length === 2 &&
      location.every((value, index) => value === [0, 0][index])
    ) {
      localStorage.setItem('allowedTracking', 'false');
    } else {
      localStorage.setItem('allowedTracking', 'true');
    }
    console.log('Location coordinates:', location);
    dispatch(signInUser({ email, password, location, id }))
      .then((response) => {
        if (response.meta.requestStatus === 'fulfilled') {
          console.log('Login successful');
          localStorage.setItem('accessToken', response.payload.AccessToken);
          localStorage.setItem('idToken', response.payload.IdToken);
          localStorage.setItem('siteId', typeof id === 'string' ? id : '');
          localStorage.setItem('userOnSite', response.payload.UserOnSite);
          dispatch(setSiteId({ siteId: typeof id === 'string' ? id : '' }));
          router.push(`/portal/acknowledgement`);
        } else {
          console.log('an error occured while signing in');
          if (response.payload.status === 403) {
            if (response.payload.message === '')
              console.log('Redirecting to reset password page...');
            window.location.href = `https://frontend-deploy-staging.dmwyzucbne4b7.amplifyapp.com/reset-password}`;
          }
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, px: 2 }}>
      <Typography
        variant="h5"
        fontWeight="bold"
        textAlign="center"
        gutterBottom
      >
        Identification Information
      </Typography>
      <Typography
        variant="body1"
        color="text.secondary"
        textAlign="center"
        gutterBottom
      >
        Please enter your email and password below.
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
        <TextField
          fullWidth
          label="Email"
          variant="filled"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{ mb: 3, backgroundColor: '#f5f5f5' }}
        />

        <TextField
          fullWidth
          label="Password"
          variant="filled"
          type={showPassword ? 'text' : 'password'}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          sx={{ mb: 4, backgroundColor: '#f5f5f5' }}
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

        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          sx={{ py: 1.5 }}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : 'CONTINUE'}
        </Button>
      </Box>

      {/* Request Account Button */}
      <Button
        variant="text"
        color="primary"
        fullWidth
        sx={{ mt: 2 }}
        onClick={() =>
          (window.location.href =
            'https://frontend-deploy-staging.dmwyzucbne4b7.amplifyapp.com/sign-up')
        }
      >
        Request Account
      </Button>
    </Container>
  );
};

export default SignInForm;
