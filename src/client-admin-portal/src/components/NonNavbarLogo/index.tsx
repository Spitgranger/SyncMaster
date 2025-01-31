import React from 'react'
import Grid from '@mui/material/Grid2';
import Image from 'next/image';
import hamiltonLogo from "../../../public/hamiltonCityLogo.svg";
import { Typography } from '@mui/material';

const NonNavbarLogo = () => {
  return (
    <Grid container direction={"column"} spacing={1}
      sx={{
        width: "100%",
        maxWidth: "552px",
        justifyContent: "center",
        alignItems: "center",
        pb: 3
      }}
    >
      <Grid size={12} textAlign={"center"}>
        <Image src={hamiltonLogo} width={160} height={139} alt='Hamilton Logo'></Image>
      </Grid>
      <Grid size={12} textAlign={"center"}>
        <Typography fontWeight={"bold"} variant='h4'>Hamilton Waterworks</Typography>
      </Grid>
    </Grid>
  )
}

export default NonNavbarLogo