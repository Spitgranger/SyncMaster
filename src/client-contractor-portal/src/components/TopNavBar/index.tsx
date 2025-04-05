import React from 'react';
import { AppBar, Toolbar, IconButton, Typography, Box } from '@mui/material';
import Image from 'next/image';
import hamiltonLogo from '../../../public/hamiltonCityLogo.svg';
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
          <Image
            src={hamiltonLogo}
            width={40}
            height={35}
            alt="Hamilton Logo"
            style={{ marginRight: 8 }}
          />
          <Typography variant="h6" fontWeight="bold">
            Hamilton Water
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default TopNavBar;
