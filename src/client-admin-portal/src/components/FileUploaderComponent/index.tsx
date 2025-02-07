//@ts-nocheck
import { Input } from "@mui/material";
import { randomUUID } from "crypto";
import { useContext, useState } from "react";
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { Dialog, DialogActions, DialogContent, DialogTitle, CircularProgress, Typography, IconButton, Box } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { DocumentTreeDispatchContext, DocumentTreeStateContext } from "@/contexts/DocumentTreeContext";

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

const FileUploaderComponent = (props) => {
    const state = useContext(DocumentTreeStateContext);
    const dispatch = useContext(DocumentTreeDispatchContext);
    const [file, setFile] = useState(null);
    const [fileName, setFileName] = useState(null);
    const [statusMessage, setStatusMessage] = useState(""); // To hold success/error message
    const [statusType, setStatusType] = useState("success"); // "success" or "error"
    const [isUploading, setIsUploading] = useState(false); // To track if uploading is in progress
    const [isDialogOpen, setIsDialogOpen] = useState(false); // To control the dialog visibility

    const uploadFile = async (fileBlob, fileName, filepath) => {
        setIsUploading(true);
        setIsDialogOpen(true);
        setStatusMessage("Uploading...");

        let isSite = null;
        let site = 'ALL'

        if (filepath.includes("sitespecific")) {
            site = filepath.split("/")[1]
        }

        try {
            console.log(fileBlob, fileName, filepath);
            const formData = new FormData();
            const s3PresignedURLResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/documents/get_presigned_url/${fileName}`, {
                method: "GET",
            });

            if (!s3PresignedURLResponse.ok) {
                throw new Error("Error in fetching presigned URL");
            }

            const s3PresignedURLResponsejson = await s3PresignedURLResponse.json();

            Object.entries(s3PresignedURLResponsejson["s3_presigned_url"]["fields"]).forEach(
                ([key, value]) => {
                    formData.append(key, value);
                }
            );

            formData.append("file", fileBlob);

            const httpResponse = await fetch(s3PresignedURLResponsejson["s3_presigned_url"]["url"], {
                method: "POST",
                body: formData,
            });

            if (!httpResponse.ok) {
                throw new Error("Error in uploading the file to S3");
            }

            const requestBody = {
                site_id: site,
                document_path: `${filepath}/${fileName}`,
                s3_key: `${fileName}`,
                e_tag: "34243245jklfjkljaklfe",
                user_id: "23432432jkljkljl",
                requires_ack: true
            };

            const requetJson = JSON.stringify(requestBody);
            const documentUploadResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/documents/upload`, {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "POST",
                body: requetJson
            });

            if (!documentUploadResponse.ok) {
                throw new Error("Error in uploading the file entry to Dynamo");
            }

            // Success case: Set success message
            setStatusMessage("File uploaded successfully!");
            setStatusType("success");

            let data = null;
            data = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/documents/${site}/get_files`)

            console.log(data);

            const jsonData = await data.json()
            console.log(jsonData);
            if (site === "ALL") {
                window.location.reload()
            } else {
                dispatch({ type: "REFRESH_DATA", payload: { data: jsonData } })
            }
        } catch (err) {
            console.log(err);
            // Error case: Set error message
            setStatusMessage("Error in uploading the file.");
            setStatusType("error");
        } finally {
            setIsUploading(false); // Stop uploading
            // setTimeout(() => {
            //     setIsDialogOpen(false); // Close the dialog after a short delay
            // }, 1500);
        }
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            const reader = new FileReader();
            reader.onload = () => {
                const byteStream = reader.result;
                const blob = new Blob([byteStream], { type: selectedFile.type });
                setFile(blob);
                setFileName(selectedFile.name);

                const isConfirmed = window.confirm(`Are you sure you want to upload the file "${selectedFile.name}"?`);
                if (isConfirmed) {
                    uploadFile(blob, selectedFile.name, props.filepath);
                } else {
                    setFile(null);
                    setFileName(null);
                }
            };

            reader.onerror = (error) => {
                console.error("Error reading file:", error);
            };

            reader.readAsArrayBuffer(selectedFile);
        }
    };

    return (
        <div className="App">
            <div>
                <Button
                    component="label"
                    role={undefined}
                    variant="contained"
                    tabIndex={-1}
                    startIcon={<CloudUploadIcon />}
                >
                    Upload file
                    <VisuallyHiddenInput
                        type="file"
                        onChange={handleFileChange}
                        multiple
                    />
                </Button>
            </div>

            {/* Dialog for showing "Uploading..." or success/error messages */}
            <Dialog
                open={isDialogOpen}
                onClose={() => setIsDialogOpen(false)}
                aria-labelledby="upload-dialog"
                aria-describedby="upload-file-status"
                sx={{ overflow: "auto" }}
            >
                <DialogTitle id="upload-dialog" width={"300px"}>
                    {isUploading ? "Uploading..." : statusType === "success" ? "Upload Successful" : "Upload Failed"}
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
                    {/* <DialogActions>
                    <IconButton
                        edge="top"
                        color="inherit"
                        onClick={() => setIsDialogOpen(false)}
                        aria-label="close"
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogActions> */}
                </DialogTitle>
                <DialogContent>
                    {isUploading ? (
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
        </div>
    );
};

export default FileUploaderComponent;