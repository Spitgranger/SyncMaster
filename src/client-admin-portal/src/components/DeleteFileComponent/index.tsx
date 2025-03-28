import React, { useState } from 'react';

import { deleteDocument, getDocuments } from '@/state/document/documentSlice'
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/state/store';
import { Button, Dialog, DialogActions, DialogContent, DialogTitle, CircularProgress, Typography, IconButton, Box } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import CloseIcon from '@mui/icons-material/Close';

interface DeleteFileComponentProps {
    site_id: string;
    parent_folder_id: string;
    document_id: string;
    idToken: string | null;
}

const DeleteFileComponent: React.FC<DeleteFileComponentProps> = ({ site_id, parent_folder_id, document_id, idToken }) => {
    const dispatch = useDispatch<AppDispatch>();
    const [isDialogOpen, setIsDialogOpen] = useState(false); // To control the dialog visibility
    const [isDeleting, setIsDeleting] = useState(false); // To track if deletion is in progress
    const [statusMessage, setStatusMessage] = useState(""); // To hold success/error message
    const [statusType, setStatusType] = useState("success"); // "success" or "error"

    console.log("delete component", document_id);


    const handleDelete = () => {
        const confirmed = window.confirm("Please confirm to proceed with the deletion");
        if (confirmed) {
            setIsDialogOpen(true);
            setIsDeleting(true);
            dispatch(deleteDocument({ site_id: site_id, parent_folder_id: parent_folder_id, document_id: document_id, idToken: idToken })).then((response) => {
                if (response.meta.requestStatus === "fulfilled") {
                    setStatusMessage("File deleted successfully");
                    setStatusType("success");
                    dispatch(getDocuments({ site_id: site_id, folder_id: parent_folder_id, idToken: idToken }));
                } else {
                    setStatusMessage("An error occurred while deleting the file");
                    setStatusType("error");
                }
                setIsDeleting(false);
            });
        }
    };

    return (
        <>
            <Button
                component="label"
                color="error"
                role={undefined}
                variant="contained"
                tabIndex={-1}
                startIcon={<DeleteIcon />}
                onClick={handleDelete}>
                Delete
            </Button>
            <Dialog
                open={isDialogOpen}
                onClose={() => setIsDialogOpen(false)}
                aria-labelledby="delete-dialog"
                aria-describedby="delete-file-status"
                sx={{ overflow: "auto" }}
            >
                <DialogTitle id="delete-dialog" width={"300px"}>
                    {isDeleting ? "Deleting..." : statusType === "success" ? "Delete Successful" : "Delete Failed"}
                    <IconButton
                        onClick={() => setIsDialogOpen(false)}
                        sx={{
                            position: 'absolute',
                            top: 10,
                            right: 10,
                            color: 'gray',
                            ml: "38px"
                        }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent>
                    {isDeleting ? (
                        <Box display="flex" justifyContent="center">
                            <CircularProgress />
                        </Box>
                    ) : (
                        <Typography variant="body1" color={statusType === "success" ? "green" : "red"} align="center">
                            {statusMessage}
                        </Typography>
                    )}
                </DialogContent>
            </Dialog>
        </>
    );
};

export default DeleteFileComponent;
