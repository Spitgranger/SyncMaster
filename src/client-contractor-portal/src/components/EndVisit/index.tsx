import React, { useState } from 'react';
import {
  Button,
  Typography,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress,
} from '@mui/material';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/state/store';
import { exitSite } from '@/state/site/siteSlice';

interface EndVisitProps {
  siteId: string | null;
  idToken: string | null;
  entryTime: string | null;
}

const EndVisit: React.FC<EndVisitProps> = ({ siteId, idToken, entryTime }) => {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null); // Track errors
  const dispatch = useDispatch<AppDispatch>();

  const handleOpenDialog = () => {
    setError(null); // Clear any previous error
    setOpen(true);
  };

  const handleCloseDialog = () => {
    setOpen(false);
    setError(null); // Reset error message
  };

  const handleEndVisit = async () => {
    setLoading(true);
    setError(null); // Clear any previous error
    dispatch(
      exitSite({ site_id: siteId, idToken: idToken, entryTime: entryTime })
    ).then((response) => {
      setLoading(false);
      if (response.meta.requestStatus === 'fulfilled') {
        handleCloseDialog();
        localStorage.clear();
        router.push('/visitended');
      } else {
        setError(
          'An error occurred while ending the visit. Would you like to try again?'
        );
      }
    });
  };

  return (
    <>
      <Button
        variant="contained"
        color="success"
        sx={{
          mt: 2,
          px: 6,
          py: 1.5,
          boxShadow: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: 1,
        }}
        onClick={handleOpenDialog}
      >
        End Visit
      </Button>
      <Dialog open={open} onClose={handleCloseDialog}>
        <DialogTitle>Confirm End Visit</DialogTitle>
        <DialogContent>
          {error ? (
            <Typography color="error">{error}</Typography>
          ) : (
            <DialogContentText>
              Are you sure you want to end your visit?
            </DialogContentText>
          )}
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseDialog}
            color="primary"
            disabled={loading}
          >
            Cancel
          </Button>
          <Button onClick={handleEndVisit} color="success" disabled={loading}>
            {loading ? <CircularProgress size={24} /> : 'Yes'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default EndVisit;
