import DashboardLayout from '@/components/layouts/DashboardLayout';
import React, { useEffect } from 'react';
import { Card, CardContent, Container, Typography } from '@mui/material';
import SiteCardComponent from '@/components/SiteCardComponent';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/state/store';
import { getSites } from '@/state/site/siteSlice';

const SitesPage = () => {
  const dispatch = useDispatch<AppDispatch>();
  const sitesState = useSelector((state: RootState) => state.site);
  const userState = useSelector((state: RootState) => state.user);
  const { idToken } = userState;

  const { sites, isLoadingSites } = sitesState;

  useEffect(() => {
    dispatch(getSites({ idToken })).then((response) => {
      if (response.meta.requestStatus === 'fulfilled') {
        console.log('Sites fetched successfully');
      } else {
        console.log('Sites fetch failed');
        console.log(response);
      }
    });
  }, [dispatch]);

  return (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        py: 6,
      }}
    >
      {sites.map((site) => (
        <SiteCardComponent key={site.id} siteId={site.site_id} />
      ))}
    </Container>
  );
};

export default SitesPage;

SitesPage.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>;
};
