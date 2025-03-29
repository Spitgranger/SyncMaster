import React from 'react';
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';
import DescriptionIcon from '@mui/icons-material/Description';
import { useRouter } from 'next/router';

const BottomNavBar = () => {
  const router = useRouter();
  const currentPath = router.pathname;
  console.log("current path",currentPath);
  

  const handleChange = (_event: React.SyntheticEvent, newValue: string) => {
    if (newValue === '/portal/jobs') {
      router.push('/portal/jobs');
    } else if (newValue === '/portal/documents') {
      router.push('/portal/documents');
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
