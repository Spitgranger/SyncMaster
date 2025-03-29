'use client'
import NonNavbarLogo from '@/components/NonNavbarLogo'
import ResetPasswordForm from '@/components/ResetPasswordForm'
import { Container } from '@mui/material'
import React from 'react'

const SignUpPage = () => {
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
            <ResetPasswordForm />
        </Container>
    )
}

export default SignUpPage