import React, { useState } from 'react';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/state/store';
import { getSiteVisitDetails, uploadAttachment } from '@/state/site/siteSlice';



interface FileUploaderComponentProps {
    siteId: string | null;
    idToken: string | null;
    entryTime: string | null;
}

const VisuallyHiddenInput = styled('input')({
    clip: 'rect(0 0 0 0)',
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
});


const FileUploaderComponent: React.FC<FileUploaderComponentProps> = ({ siteId, idToken, entryTime }) => {
    const dispatch = useDispatch<AppDispatch>();

    const [selectedFile, setSelectedFile] = useState<File | null>(null); // Single file
    const [fileBlob, setFileBlob] = useState<Blob | null>(null); // Single file blob
    const [showModal, setShowModal] = useState(false);
    const [isUploading, setIsUploading] = useState(false); // Track upload progress
    const [error, setError] = useState<string | null>(null); // Track upload errors

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            const file = event.target.files[0]; // Only handle the first file
            setSelectedFile(file);

            const reader = new FileReader();
            reader.onload = () => {
                if (reader.result) {
                    setFileBlob(new Blob([reader.result])); // Store the byte stream of the single file
                }
            };
            reader.readAsArrayBuffer(file); // Read file as byte stream

            setShowModal(true);

            // Reset the input value to allow re-selection of the same file
            event.target.value = '';
        }
    };

    const handleConfirmUpload = () => {
        console.log('Uploading file:', selectedFile);
        if (selectedFile) {
            setIsUploading(true);
            setError(null); // Clear any previous error
            dispatch(uploadAttachment({ site_id: siteId, idToken: idToken, entryTime: entryTime, fileName: selectedFile.name, fileBlob: fileBlob })).then((response) => {
                setIsUploading(false);
                if (response.meta.requestStatus === "fulfilled") {
                    console.log("File uploaded successfully");
                    dispatch(getSiteVisitDetails({ site_id: siteId, idToken: idToken, entryTime: entryTime }));
                    setShowModal(false);
                } else {
                    console.error("Failed to upload file");
                    setError("An error occurred while uploading the file. Would you like to try again?");
                }
            });
        }
    };

    const handleCancelUpload = () => {
        setSelectedFile(null);
        setFileBlob(null);
        setError(null); // Reset error message
        setShowModal(false);
    };

    return (
        <Box>
            <Button
                component="label"
                variant="contained"
                startIcon={<CloudUploadIcon />}
            >
                Upload Attachment
                <VisuallyHiddenInput
                    type="file"
                    onChange={handleFileChange} // Remove `multiple` attribute
                />
            </Button>
            <Box mt={2}>
            </Box>
            <Dialog
                open={showModal} // Ensure this is tied to the correct state
                onClose={handleCancelUpload}
                aria-labelledby="upload-dialog-title"
            >
                <DialogTitle id="upload-dialog-title">Confirm Upload</DialogTitle>
                <DialogContent>
                    {error ? (
                        <Typography color="error">{error}</Typography>
                    ) : (
                        <Typography>Do you want to upload the selected file?</Typography>
                    )}
                    <Box mt={2}>
                        {selectedFile && (
                            <Typography variant="body2">
                                {selectedFile.name}
                            </Typography>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCancelUpload} disabled={isUploading}>No</Button>
                    <Button 
                        onClick={handleConfirmUpload} 
                        variant="contained" 
                        disabled={isUploading}
                        startIcon={isUploading && <CircularProgress size={20} />}
                    >
                        {isUploading ? "Uploading..." : "Yes"}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default FileUploaderComponent;
