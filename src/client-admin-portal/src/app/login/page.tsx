'use client'
import NonNavbarLogo from '@/components/NonNavbarLogo'
import SignInForm from '@/components/SignInForm'
import { Container } from '@mui/material'
import React from 'react'

const LoginPage = () => {
    return (
        <Container
            sx={
                {
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    py: 6,
                }}
        >
            <NonNavbarLogo />
            <SignInForm />
        </Container>
    )
}

export default LoginPage