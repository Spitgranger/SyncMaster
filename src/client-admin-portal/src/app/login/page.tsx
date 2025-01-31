'use client'
import SignInComponent from '@/components/SignInComponent'
import { Container } from '@mui/material'
import React from 'react'

const LoginPage = () => {
    return (
        <Container sx={
            {
                height: "100vh",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
            }}>
            <SignInComponent />
        </Container>
    )
}

export default LoginPage