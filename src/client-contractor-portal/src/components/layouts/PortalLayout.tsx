import { AppBar, Toolbar, IconButton, Typography, Avatar, Button, Paper, Box } from '@mui/material';
import BottomNavigation from '@mui/material/BottomNavigation';
import BottomNavigationAction from '@mui/material/BottomNavigationAction';
import WorkIcon from '@mui/icons-material/Work';
import DescriptionIcon from '@mui/icons-material/Description';
import React, { useState } from 'react';
import Image from 'next/image';
import Grid from '@mui/material/Grid2';
import hamiltonLogo from '../../../public/hamiltonCityLogo.svg';
import BottomNavBar from '../BottomNavBar';
import { useRouter } from 'next/router';

interface Props {
    children: React.ReactNode;
}

export default function PortalLayout({ children }: Props) {
    const router = useRouter();
    const currentPath = router.pathname;

    const handleChange = (event: React.SyntheticEvent, newValue: string) => {
        router.push(newValue);
    };

    const isActive = (path: string) => currentPath.startsWith(path);

    return (
        <>
            <AppBar position="fixed"  sx={{boxShadow:"none", backgroundColor:"white",color:"black",borderBottom:"solid 1px black"}}>
                <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
                    <Grid container alignItems={"center"}>
                        <Grid container spacing={1} width={"168px"} display={"flex"} flexDirection={"row"}>
                            <Image src={hamiltonLogo} width={44.71} height={38} alt='Hamilton Logo' />
                            <Typography width={110} variant="body1" lineHeight={1.2} fontWeight={700} >
                                Hamilton Water
                            </Typography>
                        </Grid>
                    </Grid>
                    <Avatar />
                    {/* <Button onClick={handleSignOut}>Sign Out</Button> */}
                </Toolbar>
            </AppBar>
            <Toolbar />
                {children}
            <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
                <BottomNavigation
                    value={currentPath}
                    onChange={handleChange}
                    showLabels
                >
                    <BottomNavigationAction
                        label="Jobs"
                        value="/portal/jobs"
                        icon={<WorkIcon />}
                        sx={{ color: isActive('/portal/jobs') ? 'primary.main' : 'text.secondary' }}
                    />
                    <BottomNavigationAction
                        label="Documents"
                        value="/portal/documents"
                        icon={<DescriptionIcon />}
                        sx={{ color: isActive('/portal/documents') ? 'primary.main' : 'text.secondary' }}
                    />
                </BottomNavigation>
            </Paper>
        </>
    );
}