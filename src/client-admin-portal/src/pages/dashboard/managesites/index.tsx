"use client"
import DashboardLayout from '@/components/layouts/DashboardLayout'
import SiteCardManageComponent from '@/components/SiteCardManageComponent'
import { AppDispatch, RootState } from '@/state/store'
import { Box, Button, Container, Typography, Skeleton } from '@mui/material'
import React, { use, useEffect, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { getSites, createSite } from '@/state/site/siteSlice'
import { Dialog, DialogActions, DialogContent, DialogTitle, TextField } from '@mui/material'
import SiteComponentSkeleton from '@/components/SiteComponentSkeleton'

const ManageSites = () => {
    const dispatch = useDispatch<AppDispatch>();
    const sitesState = useSelector((state: RootState) => state.site);
    const userState = useSelector((state: RootState) => state.user);
    const { idToken } = userState;

    const { sites, isLoadingSites } = sitesState;

    const [openDialog, setOpenDialog] = useState(false);
    const [newSite, setNewSite] = useState({
        siteId: '',
        longitude: '',
        latitude: '',
        acceptableRange: ''
    });

    const [isAddingSite, setIsAddingSite] = useState(false);
    const [addSiteError, setAddSiteError] = useState<string | null>(null);

    const handleOpenDialog = () => setOpenDialog(true);
    const handleCloseDialog = () => {
        setOpenDialog(false);
        setNewSite({
            siteId: '',
            longitude: '',
            latitude: '',
            acceptableRange: ''
        });
        setAddSiteError(null);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setNewSite({ ...newSite, [name]: value });
    };

    const handleCreateSite = () => {
        setIsAddingSite(true);
        setAddSiteError(null);
        dispatch(createSite({
            idToken: idToken,
            site_id: newSite.siteId,
            longitude: parseFloat(newSite.longitude),
            latitude: parseFloat(newSite.latitude),
            acceptable_range: parseFloat(newSite.acceptableRange)
        })).then((response) => {
            setIsAddingSite(false);
            if (response.meta.requestStatus === "fulfilled") {
                console.log("Site created successfully");
                dispatch(getSites({ idToken }));
                handleCloseDialog();
            } else {
                console.log("Site creation failed");
                console.log(response);
                setAddSiteError("Failed to add site. Please try again.");
            }
        });
    };

    const isSiteIdValid = newSite.siteId.length === 5;

    useEffect(() => {
        dispatch(getSites({ idToken })).then((response) => {
            if (response.meta.requestStatus === "fulfilled") {
                console.log("Sites fetched successfully");
            }
            else {
                console.log("Sites fetch failed");
                console.log(response);
            }
        });
    }, [dispatch]);

    return (
        <>
            <Container sx={{ mt: 0, px: 0 }}>
                <Typography variant="h5" fontWeight="bold" textAlign="left" gutterBottom>
                    Manage Sites
                </Typography>
            </Container>
            <Container
                sx={
                    {
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        py: 6,
                    }}
            >
                <Box sx={{ width: "100%", maxWidth: "368px", display: "flex", justifyContent: "flex-start", mb: 2 }}>
                    <Button variant='outlined' onClick={handleOpenDialog}>+ Add New Site</Button>
                </Box>
                {isLoadingSites ? (
                    <>
                        <SiteComponentSkeleton />
                        <SiteComponentSkeleton />
                        <SiteComponentSkeleton />
                    </>
                ) : (
                    sites.map((site) => (
                        <SiteCardManageComponent key={site.site_id} siteId={site.site_id} longitude={site.longitude} latitude={site.latitude} acceptable_range={site.acceptable_range} />
                    ))
                )}
            </Container>

            <Dialog open={openDialog} onClose={handleCloseDialog}>
                <DialogTitle>Add New Site</DialogTitle>
                <DialogContent>
                    <TextField
                        margin="dense"
                        label="Site ID"
                        name="siteId"
                        fullWidth
                        value={newSite.siteId}
                        onChange={handleInputChange}
                        error={!isSiteIdValid && newSite.siteId.length > 0}
                        helperText={!isSiteIdValid && newSite.siteId.length > 0 ? "Site ID must be exactly 5 characters long" : ""}
                    />
                    <TextField
                        margin="dense"
                        label="Longitude"
                        name="longitude"
                        fullWidth
                        value={newSite.longitude}
                        onChange={handleInputChange}
                    />
                    <TextField
                        margin="dense"
                        label="Latitude"
                        name="latitude"
                        fullWidth
                        value={newSite.latitude}
                        onChange={handleInputChange}
                    />
                    <TextField
                        margin="dense"
                        label="Acceptable Range"
                        name="acceptableRange"
                        fullWidth
                        value={newSite.acceptableRange}
                        onChange={handleInputChange}
                    />
                    {isAddingSite && (
                        <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                            Adding new site...
                        </Typography>
                    )}
                    {addSiteError && (
                        <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                            {addSiteError}
                        </Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog} disabled={isAddingSite}>Cancel</Button>
                    <Button onClick={handleCreateSite} variant="contained" disabled={!isSiteIdValid || isAddingSite}>Create</Button>
                </DialogActions>
            </Dialog>
        </>
    )
}

export default ManageSites

ManageSites.getLayout = function getLayout(page: React.ReactElement) {
    return <DashboardLayout>{page}</DashboardLayout>;
}