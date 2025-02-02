'use client'
import React, { useState } from 'react'
import Grid from '@mui/material/Grid2';
import { Button, TextField, Typography } from '@mui/material';
import Link from 'next/link';

const SignInForm = () => {
    const [email, setEmail] = useState("")
    const [emailError, setEmailError] = useState(false);

    const [password, setPassword] = useState("")

    const handleEmailChange = (e: { target: { value: React.SetStateAction<string>; }; }) => {
        setEmail(e.target.value);
    }
    const handleEmailClickAway = (e: { target: { validity: { valid: boolean; }; }; }) => {
        if (e.target.validity.valid) {
            setEmailError(false);
        } else {
            setEmailError(true);
        }
    }

    const handlePasswordChange = (e: { target: { value: React.SetStateAction<string>; }; }) => {
        setPassword(e.target.value);
    }

    return (
        <Grid container boxShadow={16} direction={"column"} sx={{
            width: "100%",
            maxWidth: "552px",
            px: "24px"
        }}>
            <form onSubmit={() => { }}>
                <Grid size={12} py={2}>
                    <Typography variant='h5'>Sign In</Typography>
                </Grid>
                <Grid size={12} container direction={'column'} spacing={2} py={2}>
                    <TextField
                        type='email'
                        required
                        error={emailError}
                        name='email'
                        value={email}
                        onChange={handleEmailChange}
                        onBlur={handleEmailClickAway}
                        fullWidth
                        variant='outlined'
                        placeholder='Email'
                        helperText={emailError && 'Please enter a valid email address'} />

                    <TextField
                        type='password'
                        required
                        name='password'
                        value={password}
                        onChange={handlePasswordChange}
                        fullWidth
                        variant='outlined'
                        placeholder='Password'
                    />
                    <Link style={{textAlign:'right', color:"#1976d2"}} href={'/forgot-password'}><Typography variant='body1'>Forgot Password?</Typography></Link>

                    <Button size='large' variant='contained'>Sign In</Button>

                    <Link style={{textAlign:'center', color:"#1976d2"}} href={'/sign-up'}><Typography variant='body1'>Sign Up</Typography></Link>

                </Grid>
            </form>
        </Grid>
    )
}

export default SignInForm