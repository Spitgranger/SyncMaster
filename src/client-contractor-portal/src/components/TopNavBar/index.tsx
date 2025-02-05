import React from 'react';
import { AppBar, Toolbar, IconButton, Typography, Box } from '@mui/material';
import Image from 'next/image';
import hamiltonLogo from "../../../public/hamiltonCityLogo.svg";
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useRouter } from 'next/router';

const TopNavBar = () => {
  const router = useRouter();

  return (
    <AppBar position="static" color="transparent" elevation={1}>
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', px: 2 }}>
        {/* Logo */}
        <Box
          display="flex"
          alignItems="center"
          sx={{ cursor: 'pointer' }}
          onClick={() => router.push('/')}
        >
          <Image src={hamiltonLogo} width={40} height={35} alt="Hamilton Logo" style={{ marginRight: 8 }} />
          <Typography variant="h6" fontWeight="bold">
            Hamilton Waterworks
          </Typography>
        </Box>

        {/* Profile Button */}
        <IconButton onClick={() => router.push('/profile')}>
          <AccountCircleIcon fontSize="large" />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavBar;
