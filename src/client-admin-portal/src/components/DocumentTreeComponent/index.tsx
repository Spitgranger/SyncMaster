import React from 'react';
import Grid from '@mui/material/Grid2';

const DocumentTreeComponent = () => {
  return (
    <Grid container direction={'column'}>
      <Grid
        size={12}
        sx={{
          width: '100%',
        }}
      >
        Content
      </Grid>
      <Grid
        size={12}
        sx={{
          width: '100%',
        }}
      >
        Content
      </Grid>
    </Grid>
  );
};

export default DocumentTreeComponent;
