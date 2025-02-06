import React from 'react';
import { Button, Box, Typography, Container } from '@mui/material';

interface EndVisitButtonProps {
  onEndVisit: () => void;
}

const EndVisit: React.FC<EndVisitButtonProps> = ({ onEndVisit }) => {
  return (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        px: 3,
      }}
    >
      <Typography variant="h6" color="text.secondary" textAlign="center" gutterBottom>
        Kindly remember to end your session before leaving the site.
      </Typography>
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
        onClick={onEndVisit}
      >
        End Visit
      </Button>
    </Container>
  );
};

export default EndVisit;
