import { Box, Typography, Modal, Button, CircularProgress } from '@mui/material'
import React, { useState } from 'react'
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DeleteIcon from '@mui/icons-material/Delete';
import theme from '@/theme';
import Link from 'next/link';
import { AppDispatch, RootState } from '@/state/store';
import { useDispatch, useSelector } from 'react-redux';
import { getSiteVisitDetails, removeAttachment } from '@/state/site/siteSlice';

interface FileAttachmentComponentProps {
    attachment: {
        name: string;
        url: string;
    };
}

const FileAttachmentComponent = ({ attachment }: FileAttachmentComponentProps) => {
    const [open, setOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const dispatch = useDispatch<AppDispatch>();
    const { idToken, siteId } = useSelector((state: RootState) => state.user);
    const { entryTime } = useSelector((state: RootState) => state.site);
    const handleOpen = () => setOpen(true);
    const handleClose = () => {
        if (!isDeleting) {
            setError(null); // Reset error message
            setOpen(false);
        }
    };
    const handleDelete = () => {
        setIsDeleting(true);
        setError(null); // Clear any previous error
        dispatch(removeAttachment({ site_id: siteId, idToken: idToken, entryTime: entryTime, fileName: attachment.name })).then((response) => {
            setIsDeleting(false);
            if (response.meta.requestStatus === "fulfilled") {
                console.log("File deleted successfully");
                dispatch(getSiteVisitDetails({ site_id: siteId, idToken: idToken, entryTime: entryTime }));
                setOpen(false); // Close modal after successful deletion
            } else {
                console.error("Error deleting file");
                setError("An error occurred while deleting the file. Please try again.");
            }
        });
    };

    return (
        <>
            <Box sx={{ display: "flex", justifyContent: "space-between", p: 2, boxShadow: 3, mb: 2 }}>
                <UploadFileIcon color='primary' sx={{ mr: 2 }}></UploadFileIcon>
                <Box flexGrow={1} textAlign={"left"}>
                    <Typography variant='body1' sx={{ ml: 1 }}>
                        <Link href={attachment.url}>{attachment.name}</Link>
                    </Typography>
                </Box>
                <DeleteIcon
                    sx={{ ml: 2, color: theme.palette.grey[600], cursor: 'pointer' }}
                    onClick={handleOpen}
                ></DeleteIcon>
            </Box>
            <Modal
                open={open}
                onClose={handleClose}
                aria-labelledby="delete-confirmation-title"
                aria-describedby="delete-confirmation-description"
            >
                <Box sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 300,
                    bgcolor: 'background.paper',
                    boxShadow: 24,
                    p: 4,
                    borderRadius: 2,
                }}>
                    <Typography id="delete-confirmation-title" variant="h6" component="h2">
                        Confirm Deletion
                    </Typography>
                    <Typography id="delete-confirmation-description" sx={{ mt: 2 }}>
                        {error ? (
                            <Typography color="error">{error}</Typography>
                        ) : (
                            "Are you sure you want to delete this file?"
                        )}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
                        <Button onClick={handleClose} sx={{ mr: 2 }} disabled={isDeleting}>Cancel</Button>
                        <Button 
                            onClick={handleDelete} 
                            color="error" 
                            variant="contained" 
                            disabled={isDeleting}
                            startIcon={isDeleting && <CircularProgress size={20} />}
                        >
                            {isDeleting ? "Deleting..." : "Delete"}
                        </Button>
                    </Box>
                </Box>
            </Modal>
        </>
    )
}

export default FileAttachmentComponent