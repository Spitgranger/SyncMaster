import { AppBar, Toolbar, IconButton, Typography, Avatar, Button, Paper, Box, Menu, MenuItem, Divider } from '@mui/material';
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
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/state/store';
import { signOutUser } from '@/state/user/userSlice';

interface Props {
    children: React.ReactNode;
}

export default function PortalLayout({ children }: Props) {
    const router = useRouter();
    const dispatch = useDispatch<AppDispatch>();
    const userState = useSelector((state: RootState) => state.user);
    const { username, role, siteId } = userState;

    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const openMenu = Boolean(anchorEl);

    const handleAvatarClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const handleSignOutClick = () => {
        handleMenuClose();
        handleSignOut({ preventDefault: () => {} } as React.MouseEvent<HTMLButtonElement>);
    };

    function handleSignOut(event: React.MouseEvent<HTMLButtonElement>): void {
        event.preventDefault();
        dispatch(signOutUser()).then((response) => {
            if (response.meta.requestStatus === "fulfilled") {
                localStorage.clear();
                router.push(`/login?id=${siteId}`);
            } else {
                console.log("An error occurred while signing out");
                console.log(response);
            }
        });
    }

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
                    <IconButton onClick={handleAvatarClick}>
                        <Avatar />
                    </IconButton>
                    <Menu
                        anchorEl={anchorEl}
                        open={openMenu}
                        onClose={handleMenuClose}
                        anchorOrigin={{
                            vertical: 'bottom',
                            horizontal: 'right',
                        }}
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'right',
                        }}
                    >
                        <Box px={2} py={1}>
                            <Typography variant="body2" color="black" fontWeight="bold" sx={{ mb: 1 }}>Name: {username}</Typography>
                            <Typography variant="body2" color="black" sx={{ mb: 1 }}>Role: {role}</Typography>
                        </Box>
                        <Divider />
                        <MenuItem onClick={handleSignOutClick}>Sign Out</MenuItem>
                    </Menu>
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