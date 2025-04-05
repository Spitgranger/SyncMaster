//@ts-nocheck
import { Input } from '@mui/material';
import { randomUUID } from 'crypto';
import { useContext, useState } from 'react';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  CircularProgress,
  Typography,
  IconButton,
  Box,
  Menu,
  MenuItem,
  TextField,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import AddIcon from '@mui/icons-material/Add';
import {
  DocumentTreeDispatchContext,
  DocumentTreeStateContext,
} from '@/contexts/DocumentTreeContext';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '@/state/store';
import { uploadDocument, getDocuments } from '@/state/document/documentSlice';

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

export default function FileUploaderComponent(props: {
  site_id: any;
  parent_folder_id: any;
  document_path: any;
  user_id: any;
  idToken: any;
}) {
  const { site_id, parent_folder_id, document_path, user_id, idToken } = props;
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [statusMessage, setStatusMessage] = useState(''); // To hold success/error message
  const [statusType, setStatusType] = useState('success'); // "success" or "error"
  const [isUploading, setIsUploading] = useState(false); // To track if uploading is in progress
  const [isDialogOpen, setIsDialogOpen] = useState(false); // To control the dialog visibility
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null); // For context menu
  const [isFolderDialogOpen, setIsFolderDialogOpen] = useState(false); // For folder creation modal
  const [folderName, setFolderName] = useState(''); // To hold folder name input
  const [expiryDate, setExpiryDate] = useState(''); // To hold the document expiry date
  const [requiresAcknowledgement, setRequiresAcknowledgement] = useState(false); // To track acknowledgment requirement
  const [isFolderUploading, setIsFolderUploading] = useState(false); // To track folder upload status
  const [folderUploadStatusMessage, setFolderUploadStatusMessage] =
    useState(''); // To hold folder upload status message
  const [folderUploadStatusType, setFolderUploadStatusType] =
    useState('success'); // "success" or "error"
  const dispatch = useDispatch<AppDispatch>();

  const handleMenuClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAddFolder = () => {
    setIsFolderDialogOpen(true);
    handleMenuClose();
  };

  const handleFolderCreation = () => {
    if (folderName.trim()) {
      console.log('Creating folder:', folderName);
      setIsFolderUploading(true); // Set folder uploading state
      setFolderUploadStatusMessage(''); // Reset status message

      // Dispatch the upload operation for folder creation
      dispatch(
        uploadDocument({
          site_id: site_id,
          document_name: folderName, // Use folderName as the document name
          document_type: 'folder', // Specify type as folder
          parent_folder_id: parent_folder_id,
          document_path: document_path,
          user_id: user_id,
          idToken: idToken,
          requires_ack: false, // Set requires_ack to false
          document_expiry: null, // Set expiry date to null
          fileBlob: null, // No file blob for folder creation
        })
      ).then((response) => {
        if (response.meta.requestStatus === 'fulfilled') {
          setFolderUploadStatusMessage('Folder Created Successfully');
          setFolderUploadStatusType('success');
          setIsFolderUploading(false); // Stop folder uploading state
          setIsFolderDialogOpen(false); // Close the dialog only on success
          setFolderName('');
          dispatch(
            getDocuments({
              site_id: site_id,
              folder_id: parent_folder_id,
              idToken: idToken,
            })
          );
        } else {
          console.log('An error occurred while creating the folder');
          console.log(response);
          setFolderUploadStatusMessage('Folder Creation Failed');
          setFolderUploadStatusType('error');
          setIsFolderUploading(false); // Stop folder uploading state
          // Keep the dialog open on failure
        }
      });
    }
  };

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = () => {
        const byteStream = reader.result;
        const blob = new Blob([byteStream], { type: selectedFile.type });
        setFile(blob);
        setFileName(selectedFile.name); // Ensure fileName is updated
        setIsDialogOpen(true); // Directly open the modal
        e.target.value = ''; // Reset the input value to allow re-upload
      };

      reader.onerror = (error) => {
        console.error('Error reading file:', error);
      };

      reader.readAsArrayBuffer(selectedFile);
    }
  };

  const handleUpload = () => {
    const expiryDateValue = expiryDate || null; // Pass null if no expiry date is provided

    setIsUploading(true);
    setStatusMessage(''); // Reset status message

    dispatch(
      uploadDocument({
        site_id: site_id,
        document_name: fileName, // Use fileName directly
        document_type: 'file',
        parent_folder_id: parent_folder_id,
        document_path: document_path,
        user_id: user_id,
        idToken: idToken,
        requires_ack: requiresAcknowledgement, // Include acknowledgment requirement
        fileBlob: file,
        document_expiry: expiryDateValue, // Include expiry date or null
      })
    ).then((response) => {
      if (response.meta.requestStatus === 'fulfilled') {
        setStatusMessage('Upload Successful');
        setStatusType('success');
        dispatch(
          getDocuments({
            site_id: site_id,
            folder_id: parent_folder_id,
            idToken: idToken,
          })
        );
        setIsDialogOpen(false); // Close the dialog on success
      } else {
        console.log('An error occurred while uploading the file');
        console.log(response);
        setStatusMessage('Upload Failed');
        setStatusType('error');
      }
      setIsUploading(false);
    });
  };

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const today = formatDate(new Date()); // Get today's date in "YYYY-MM-DD" format

  const handleCloseFileDialog = () => {
    if (!isUploading) {
      setIsDialogOpen(false);
      setStatusMessage(''); // Reset file upload error message
      setStatusType('success'); // Reset status type
    }
  };

  const handleCloseFolderDialog = () => {
    if (!isFolderUploading) {
      setIsFolderDialogOpen(false);
      setFolderUploadStatusMessage(''); // Reset folder upload error message
      setFolderUploadStatusType('success'); // Reset status type
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
          startIcon={<AddIcon />}
          onClick={handleMenuClick}
        >
          Add New
        </Button>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem>
            <label style={{ cursor: 'pointer', width: '100%' }}>
              Add File
              <VisuallyHiddenInput
                type="file"
                onClick={(e) => e.stopPropagation()} // Prevent onClick from interfering
                onChange={(e) => {
                  handleFileChange(e); // Ensure file upload logic is triggered
                  handleMenuClose(); // Close menu after selecting a file
                }}
                multiple
              />
            </label>
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleAddFolder();
              handleMenuClose(); // Close menu when "Add Folder" is clicked
            }}
          >
            Add Folder
          </MenuItem>
        </Menu>
      </div>
      <Dialog
        open={isFolderDialogOpen}
        onClose={handleCloseFolderDialog} // Use the new handler
        aria-labelledby="folder-dialog"
      >
        <DialogTitle id="folder-dialog">
          {isFolderUploading ? 'Creating Folder...' : 'Create New Folder'}
        </DialogTitle>
        <DialogContent>
          {isFolderUploading ? (
            <Box display="flex" justifyContent="center">
              <CircularProgress />
            </Box>
          ) : (
            <>
              <TextField
                autoFocus
                margin="dense"
                label="Folder Name"
                type="text"
                fullWidth
                value={folderName}
                onChange={(e) => setFolderName(e.target.value)}
              />
              {folderUploadStatusMessage && (
                <Typography
                  variant="body2"
                  color={folderUploadStatusType === 'success' ? 'green' : 'red'}
                  align="center"
                  mt={2}
                >
                  {folderUploadStatusMessage}
                </Typography>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          {!isFolderUploading && (
            <>
              <Button onClick={handleCloseFolderDialog}>Cancel</Button>
              <Button onClick={handleFolderCreation} variant="contained">
                Create
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
      <Dialog
        open={isDialogOpen}
        onClose={handleCloseFileDialog} // Use the new handler
        aria-labelledby="upload-dialog"
        aria-describedby="upload-file-status"
        sx={{ overflow: 'auto' }}
      >
        <DialogTitle id="upload-dialog" width={'300px'}>
          {isUploading ? 'Uploading...' : 'Confirm Upload'}
          <IconButton
            onClick={handleCloseFileDialog} // Use the new handler
            sx={{
              position: 'absolute',
              top: 10,
              right: 10,
              color: 'gray',
              ml: '38px',
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {isUploading ? (
            <Box display="flex" justifyContent="center">
              <CircularProgress />
            </Box>
          ) : (
            <>
              <Typography variant="body1" align="center">
                File Name: {fileName}
              </Typography>
              {statusMessage && (
                <Typography
                  variant="body2"
                  color={statusType === 'success' ? 'green' : 'red'}
                  align="center"
                  mt={2}
                >
                  {statusMessage}
                </Typography>
              )}
              <Box mt={2}>
                <TextField
                  label="Expiry Date"
                  type="date"
                  fullWidth
                  InputLabelProps={{
                    shrink: true,
                  }}
                  value={expiryDate}
                  onChange={(e) => setExpiryDate(e.target.value)}
                  inputProps={{
                    min: today, // Prevent selecting a past date
                  }}
                />
                <Typography variant="caption" color="textSecondary">
                  Note: Leave blank if no expiry date is required
                </Typography>
              </Box>
              <Box mt={2}>
                <FormControl component="fieldset">
                  <FormLabel component="legend">
                    Does this document require acknowledgment?
                  </FormLabel>
                  <RadioGroup
                    row
                    value={requiresAcknowledgement}
                    onChange={(e) =>
                      setRequiresAcknowledgement(e.target.value === 'true')
                    }
                  >
                    <FormControlLabel
                      value={true}
                      control={<Radio />}
                      label="Yes"
                    />
                    <FormControlLabel
                      value={false}
                      control={<Radio />}
                      label="No"
                    />
                  </RadioGroup>
                </FormControl>
              </Box>
            </>
          )}
        </DialogContent>
        <DialogActions>
          {!isUploading && (
            <>
              <Button onClick={handleCloseFileDialog}>Cancel</Button>
              <Button onClick={handleUpload} variant="contained">
                Upload
              </Button>
            </>
          )}
        </DialogActions>
      </Dialog>
    </div>
  );
}
