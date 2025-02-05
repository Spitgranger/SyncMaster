import React from 'react';
import { Button, Box, Typography } from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

type AddNewJobButtonProps = {
  onAddJob: () => void;
};

const AddJob: React.FC<AddNewJobButtonProps> = ({ onAddJob }) => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      sx={{ mt: 4, width: '100%' }}
    >
      <Typography variant="h6" color="text.secondary" gutterBottom>
        No Jobs found
      </Typography>
      <Button
        variant="contained"
        color="success"
        startIcon={<AddCircleOutlineIcon sx={{ fontSize: '1.2rem' }} />}
        sx={{
          mt: 2,
          px: 4,
          py: 1.5,
          boxShadow: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: 1, // Adjust spacing between icon and text
        }}
        onClick={onAddJob}
      >
        ADD NEW JOB
      </Button>
    </Box>
  );
};

export default AddJob;