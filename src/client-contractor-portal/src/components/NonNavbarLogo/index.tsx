import React from 'react';
import Grid from '@mui/material/Grid2';
import Image from 'next/image';
import hamiltonLogo from '../../../public/hamiltonCityLogo.svg';
import { Typography } from '@mui/material';

const NonNavbarLogo = () => {
  return (
    <Grid
      container
      direction="row"
      alignItems="center"
      spacing={2}
      sx={{
        width: '100%',
        maxWidth: '552px',
        justifyContent: 'center',
        pb: 3,
      }}
    >
      <Grid>
        <Image src={hamiltonLogo} width={80} height={69} alt="Hamilton Logo" />
      </Grid>
      <Grid>
        <Typography fontWeight="bold" variant="h4">
          Hamilton Water
        </Typography>
      </Grid>
    </Grid>
  );
};

export default NonNavbarLogo;
