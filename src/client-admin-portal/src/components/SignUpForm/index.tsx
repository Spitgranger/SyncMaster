'use client';
import React, { useState } from 'react';
import Grid from '@mui/material/Grid2';
import { Button, TextField, Typography, MenuItem } from '@mui/material';
import Link from 'next/link';
import { useDispatch } from 'react-redux';
import { createAccountRequest } from '@/state/user/userRequestsSlice';
import { AppDispatch } from '@/state/store';

const SignUpForm = () => {
  const dispatch = useDispatch<AppDispatch>();

  const [email, setEmail] = useState('');
  const [company, setCompany] = useState('');
  const [name, setName] = useState('');
  const [roleRequested, setRoleRequested] = useState('contractor'); // default value

  const [emailError, setEmailError] = useState(false);
  const [formError, setFormError] = useState('');
  const [isSignUpButtonDisabled, setIsSignUpButtonDisabled] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  // Optional: a separate state for the success message
  const [successMessage, setSuccessMessage] = useState('');

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

  const handleCompanyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCompany(e.target.value);
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
  };

  const handleRoleRequestedChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setRoleRequested(e.target.value);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSignUpButtonDisabled(true);
    setFormError('');

    try {
      const response = await dispatch(
        createAccountRequest({
          email,
          company,
          name,
          role_requested: roleRequested,
        })
      );
      if (response.meta.requestStatus === 'fulfilled') {
        // Instead of redirecting, display a success message on the same page
        setSuccessMessage(
          'Your submission has been received and is pending review by our team.'
        );
        setSubmitted(true);
      } else {
        setFormError('An error occurred while creating the account request.');
      }
    } catch (error) {
      setFormError('An error occurred while creating the account request.');
    }
    setIsSignUpButtonDisabled(false);
  };

  return (
    <Grid
      container
      boxShadow={16}
      direction="column"
      sx={{ width: '100%', maxWidth: '552px', px: '24px' }}
    >
      {submitted ? (
        <Grid py={2}>
          <Typography variant="h5">Account Request Received</Typography>
          <Typography variant="body1">{successMessage}</Typography>
        </Grid>
      ) : (
        <form onSubmit={handleSubmit}>
          <Grid py={2}>
            <Typography variant="h5">Request Account</Typography>
          </Grid>
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
                type="text"
                required
                name="company"
                value={company}
                onChange={handleCompanyChange}
                fullWidth
                variant="outlined"
                placeholder="Company"
              />
            </Grid>
            <Grid>
              <TextField
                type="text"
                required
                name="name"
                value={name}
                onChange={handleNameChange}
                fullWidth
                variant="outlined"
                placeholder="Name"
              />
            </Grid>
            <Grid>
              <TextField
                select
                required
                name="role_requested"
                value={roleRequested}
                onChange={handleRoleRequestedChange}
                fullWidth
                variant="outlined"
                label="Role Requested"
              >
                <MenuItem value="contractor">Contractor</MenuItem>
                <MenuItem value="employee">Employee</MenuItem>
              </TextField>
            </Grid>
            {formError && (
              <Grid>
                <Typography color="error" variant="body2">
                  {formError}
                </Typography>
              </Grid>
            )}
            <Grid display="flex" justifyContent="center">
              <Button
                disabled={isSignUpButtonDisabled}
                type="submit"
                size="large"
                variant="contained"
              >
                Request Account
              </Button>
            </Grid>
            <Grid display="flex" justifyContent="center">
              <Link href="/login">
                <Typography variant="body1">Back to Sign In</Typography>
              </Link>
            </Grid>
          </Grid>
        </form>
      )}
    </Grid>
  );
};

export default SignUpForm;
