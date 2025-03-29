import React, { useState, useRef } from 'react';
import { Box, Button, Typography, CircularProgress, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, TextField } from '@mui/material';
import Grid from '@mui/material/Grid2';
import ApartmentIcon from '@mui/icons-material/Apartment';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import QrCode2Icon from '@mui/icons-material/QrCode2';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/state/store';
import { deleteSite, getSites, updateSite } from '@/state/site/siteSlice';
import { QRCodeCanvas } from 'qrcode.react';

const SiteCardManageComponent = ({
  siteId,
  longitude,
  latitude,
  acceptable_range
}: {
  siteId: string,
  longitude: number,
  latitude: number,
  acceptable_range: number
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editSite, setEditSite] = useState({
    siteId,
    longitude: longitude.toString(),
    latitude: latitude.toString(),
    acceptableRange: acceptable_range.toString(),
  });

  // Control the QR code dialog
  const [isQRModalOpen, setIsQRModalOpen] = useState(false);

  // IMPORTANT: Use a ref to capture the <canvas> element from QRCodeCanvas
  const qrRef = useRef<HTMLCanvasElement>(null);

  const clientUrl = process.env.NEXT_PUBLIC_API_CONTRACTOR_BASE_URL;
  const dispatch = useDispatch<AppDispatch>();
  const { idToken } = useSelector((state: RootState) => state.user);

  const handleDeleteClick = () => {
    setIsModalOpen(true);
  };

  const handleEditClick = () => {
    setIsEditModalOpen(true);
  };

  const handleOpenQRModal = () => {
    setIsQRModalOpen(true);
  };

  const handleCloseQRModal = () => {
    setIsQRModalOpen(false);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setIsDeleting(false);
    setError(null);
  };

  const handleCloseEditModal = () => {
    setIsEditModalOpen(false);
    setError(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditSite({ ...editSite, [name]: value });
  };

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    setError(null);
    dispatch(deleteSite({ idToken: idToken, site_id: siteId })).then((response) => {
      if (response.meta.requestStatus === "fulfilled") {
        console.log("Site deleted successfully");
        dispatch(getSites({ idToken }));
        handleCloseModal();
      } else {
        setError("Failed to delete the site. Do you want to try again?");
        setIsDeleting(false);
      }
    });
  };

  const handleSaveEdit = () => {
    setError(null);
    setIsEditing(true);
    dispatch(updateSite({
      idToken: idToken,
      site_id: editSite.siteId,
      longitude: parseFloat(editSite.longitude),
      latitude: parseFloat(editSite.latitude),
      acceptable_range: parseFloat(editSite.acceptableRange)
    })).then((response) => {
      setIsEditing(false);
      if (response.meta.requestStatus === "fulfilled") {
        console.log("Site edited successfully");
        dispatch(getSites({ idToken }));
        setIsEditModalOpen(false);
      } else {
        console.log("Failed to edit site");
        setError("Failed to edit the site. Please try again.");
      }
    });
  };

  // Function to download the QR code as an image (PNG)
  const handleDownloadQRCode = () => {
    if (!qrRef.current) return;

    // Convert the canvas content to a DataURL
    const dataUrl = qrRef.current.toDataURL("image/png");

    // Create an <a> tag and trigger download
    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = `site-${siteId}-qr.png`; // File name
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Grid
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
        mb: 3
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center" }}>
        <ApartmentIcon
          sx={{ width: "48px", height: "48px", color: "black", opacity: "56%", mr: 2 }}
        />
        <Typography variant="body1" fontWeight="bold">
          Site ID: {siteId}
        </Typography>
      </Box>
      <Box>
        <EditIcon sx={{ mr: 2, cursor: "pointer" }} onClick={handleEditClick} />
        <DeleteIcon sx={{ mr: 2, cursor: "pointer" }} onClick={handleDeleteClick} />
        <QrCode2Icon sx={{ cursor: "pointer" }} onClick={handleOpenQRModal} />

        {/* Confirm Deletion Dialog */}
        <Dialog open={isModalOpen} onClose={handleCloseModal}>
          <DialogTitle>Confirm Deletion</DialogTitle>
          <DialogContent>
            {isDeleting ? (
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <CircularProgress size={24} />
                <Typography sx={{ ml: 2 }}>Deleting...</Typography>
              </Box>
            ) : error ? (
              <DialogContentText color="error">{error}</DialogContentText>
            ) : (
              <DialogContentText>
                Are you sure you want to delete this site?
              </DialogContentText>
            )}
          </DialogContent>
          {!isDeleting && (
            <DialogActions>
              <Button onClick={handleConfirmDelete} color="error">Yes</Button>
              <Button onClick={handleCloseModal}>No</Button>
            </DialogActions>
          )}
        </Dialog>

        {/* Edit Site Dialog */}
        <Dialog open={isEditModalOpen} onClose={handleCloseEditModal}>
          <DialogTitle>Edit Site</DialogTitle>
          <DialogContent>
            <TextField
              margin="dense"
              label="Site ID"
              name="siteId"
              fullWidth
              value={editSite.siteId}
              onChange={handleInputChange}
              disabled
            />
            <TextField
              margin="dense"
              label="Latitude"
              name="latitude"
              fullWidth
              value={editSite.latitude}
              onChange={handleInputChange}
              helperText="degrees (°)"
            />
            <TextField
              margin="dense"
              label="Longitude"
              name="longitude"
              fullWidth
              value={editSite.longitude}
              onChange={handleInputChange}
              helperText="degrees (°)"
            />
            <TextField
              margin="dense"
              label="Acceptable Range"
              name="acceptableRange"
              fullWidth
              value={editSite.acceptableRange}
              onChange={handleInputChange}
              helperText="meters (m)"
            />
            {isEditing && (
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                Saving changes...
              </Typography>
            )}
            {error && (
              <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                {error}
              </Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseEditModal} disabled={isEditing}>
              Cancel
            </Button>
            <Button onClick={handleSaveEdit} variant="contained" disabled={isEditing}>
              Save
            </Button>
          </DialogActions>
        </Dialog>

        {/* QR Code Dialog */}
        <Dialog open={isQRModalOpen} onClose={handleCloseQRModal}>
          <DialogTitle>Site QR Code</DialogTitle>
          <DialogContent>
            <Box sx={{ textAlign: "center", mt: 2 }}>
              {/* Add ref to capture the <canvas> element */}
              <QRCodeCanvas
                ref={qrRef}
                value={`${clientUrl}?id=${siteId}`}
                size={300}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseQRModal}>Close</Button>
            {/* Save Image Button */}
            <Button onClick={handleDownloadQRCode}>
              Save Image
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Grid>
  );
};

export default SiteCardManageComponent;
