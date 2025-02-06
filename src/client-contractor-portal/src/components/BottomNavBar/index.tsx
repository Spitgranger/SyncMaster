import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';
import DescriptionIcon from '@mui/icons-material/Description';
import { useRouter } from 'next/router';

const BottomNavBar = () => {
  const router = useRouter();
  const currentPath = router.pathname;

  const handleChange = (_event: React.SyntheticEvent, newValue: string) => {
    if (newValue === '/jobs') {
      router.push('/jobs');
    } else if (newValue === '/documents') {
      router.push('/documents');
    }
  };

  return (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
      <BottomNavigation
        value={currentPath}
        onChange={handleChange}
        showLabels
      >
        <BottomNavigationAction
          label="Jobs"
          value="/jobs"
          icon={<WorkIcon />}
        />
        <BottomNavigationAction
          label="Documents"
          value="/documents"
          icon={<DescriptionIcon />}
        />
      </BottomNavigation>
    </Paper>
  );
};

export default BottomNavBar;
