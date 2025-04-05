import React from 'react';
import { Box, Typography } from '@mui/material';
import Grid from '@mui/material/Grid2';
import ApartmentIcon from '@mui/icons-material/Apartment';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { useRouter } from 'next/router';

const SiteCardComponent = ({ siteId }: { siteId: string }) => {
  const router = useRouter();

  const handleNavigate = () => {
    router.push(`/dashboard/sitespecific/${siteId}`);
  };

  return (
    <Grid
      onClick={handleNavigate}
      sx={{
        width: "100%",
        maxWidth: "368px",
        border: "1px solid black",
        borderRadius: "8px",
        px: 2,
        py: 1,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        mb: 3,
        cursor: "pointer"
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <ApartmentIcon sx={{ width: "48px", height: "48px", color: "black", opacity: "56%", mr: 2 }} />
        <Typography variant="body1" fontWeight="bold">
          Site ID: {siteId}
        </Typography>
      </Box>
      <ChevronRightIcon sx={{ width: "24px", height: "24px" }} />
    </Grid>
  );
};

export default SiteCardComponent;
