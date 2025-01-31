'use client'
import NonNavLogoComponent from '@/components/nonNavLogoComponent'
import SignInComponent from '@/components/SignInComponent'
import { Container } from '@mui/material'
import React from 'react'

const LoginPage = () => {
    return (
        <Container sx={
            {
                height: "100vh",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                py: 6,
                overflowY: "auto"
            }}>
            <NonNavLogoComponent />
            <SignInComponent />
        </Container>
    )
}

export default LoginPage