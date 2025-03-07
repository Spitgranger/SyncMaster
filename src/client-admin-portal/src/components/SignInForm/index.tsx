'use client'
import React, { useState } from 'react'
import Grid from '@mui/material/Grid2';
import { Button, IconButton, InputAdornment, TextField, Typography } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import Link from 'next/link';
import { signInUser } from '@/services/userService';
import { useRouter } from 'next/navigation';

const SignInForm = () => {
    const [email, setEmail] = useState("")
    const [emailError, setEmailError] = useState(false);

    const [password, setPassword] = useState("")
    const [showPassword, setShowPassword] = useState(false);

    const router = useRouter();

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
    const handleClickShowPassword = () => setShowPassword((show) => !show);
    const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
    };

    const handleMouseUpPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        try {
            const result = await signInUser(email, password);
            localStorage.setItem("accessToken", result.AccessToken);
            localStorage.setItem("IdToken", result.IdToken);
            console.log("Signed in successfully", result);
            router.push('/dashboard/sitewide');
        } catch (error) {
            console.error("Sign in failed", error);
        }
    }

    return (
        <Grid container boxShadow={16} direction={"column"} sx={{
            width: "100%",
            maxWidth: "552px",
            px: "24px"
        }}>
            <form onSubmit={handleSubmit}>
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
                        type={showPassword ? 'text' : 'password'}
                        required
                        name='password'
                        value={password}
                        onChange={handlePasswordChange}
                        fullWidth
                        variant='outlined'
                        placeholder='Password'
                        slotProps={{
                            input: {
                                endAdornment: (
                                    <InputAdornment position='end'>
                                        <IconButton
                                            aria-label={showPassword ? 'hide the password' : 'display the password'}
                                            onClick={handleClickShowPassword}
                                            onMouseDown={handleMouseDownPassword}
                                            onMouseUp={handleMouseUpPassword}
                                        >
                                            {showPassword ? <Visibility /> : <VisibilityOff />}
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }
                        }}
                    />
                    <Grid display={"flex"} justifyContent={"flex-end"}>
                        <Link style={{ textAlign: 'right', color: "#1976d2" }} href={'/forgot-password'}>
                            <Typography variant='body1'>Forgot Password?</Typography>
                        </Link>
                    </Grid>

                    <Button type="submit" size='large' variant='contained'>Sign In</Button>

                    <Grid display={"flex"} justifyContent={"center"}>
                        <Link style={{ textAlign: 'center', color: "#1976d2" }} href={'/sign-up'}>
                            <Typography variant='body1'>Sign Up</Typography>
                        </Link>
                    </Grid>
                </Grid>
            </form>
        </Grid>
    )
}

export default SignInForm
