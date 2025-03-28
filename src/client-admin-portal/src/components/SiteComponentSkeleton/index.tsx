import { Box, Typography } from '@mui/material'
import Grid from '@mui/material/Grid2';
import React from 'react'

const SiteComponentSkeleton = () => {
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
                <Box sx={{ width: "48px", height: "48px", backgroundColor: "grey.300", mr: 2 }} />
                <Typography variant="body1" fontWeight="bold" sx={{ backgroundColor: "grey.300", width: "100px", height: "24px", borderRadius: "4px" }}></Typography>
            </Box>
            <Box display={"flex"}>
                <Box sx={{ width: "24px", height: "24px", backgroundColor: "grey.300", borderRadius: "50%", mr: 2 }} />
                <Box sx={{ width: "24px", height: "24px", backgroundColor: "grey.300", borderRadius: "50%" }} />
            </Box>
        </Grid>
    )
}

export default SiteComponentSkeleton