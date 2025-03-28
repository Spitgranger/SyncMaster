import React from 'react'
import { Box, Typography } from '@mui/material'
import Grid from '@mui/material/Grid2';
import ApartmentIcon from '@mui/icons-material/Apartment';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { useRouter } from 'next/router'; // Updated import

const SiteCardComponent = ({ siteId }: { siteId: string }) => {
    const router = useRouter(); // Updated to useRouter

    const handleNavigate = () => {
        router.push(`/dashboard/sitespecific/${siteId}`); // Updated navigation logic
    };

    return (
        <Grid sx={{
            width: "100%",
            maxWidth: "368px",
            border: "1px solid black",
            borderRadius: "8px",
            px: 2,
            py: 1,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 3
        }} >
            <Box sx={{ display: "flex", alignItems: "center" }}>
                <ApartmentIcon sx={{ width: "48px", height: "48px", color: "black", opacity: "56%", mr: 2 }} />
                <Typography variant="body1" fontWeight="bold">Site ID: {siteId}</Typography>
            </Box>
            <ChevronRightIcon 
                sx={{ width: "24px", height: "24px", cursor: "pointer" }} 
                onClick={handleNavigate} // Updated click handler
            />
        </Grid>
    )
}

export default SiteCardComponent