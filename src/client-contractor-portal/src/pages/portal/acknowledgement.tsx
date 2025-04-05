'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';
import { Container } from '@mui/material';
import AcknowledgmentForm from '@/components/AcknowledgementForm';
import NonNavbarLogo from '@/components/NonNavbarLogo';
import { AppDispatch } from '@/state/store';
import { useDispatch, useSelector } from 'react-redux';
import { getAcknowledgementDocuments } from '@/state/document/documentSlice';
import { RootState } from '@/state/store';
import { sign } from 'crypto';
import { signOutUser } from '@/state/user/userSlice';
import { enterSite, setEntryTime } from '@/state/site/siteSlice';
import CircularProgress from '@mui/material/CircularProgress';

const AcknowledgementPage = () => {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const { idToken, siteId } = useSelector((state: RootState) => state.user);
  const { isLoading, acknowledgementDocuments } = useSelector(
    (state: RootState) => state.document
  );
  const { isEnteringOrExitingSite } = useSelector(
    (state: RootState) => state.site
  );

  const handleProceed = async ({
    acknowledgedAll,
    hasCompletedTraining,
    accompaniedByEmployee,
    employeeID,
  }: {
    acknowledgedAll: boolean;
    hasCompletedTraining: boolean;
    accompaniedByEmployee: boolean;
    employeeID: string | null;
  }) => {
    console.log('Proceeding with the following data:', {
      acknowledgedAll,
      hasCompletedTraining,
      accompaniedByEmployee,
      employeeID,
    });

    const proceedAction = () => {
      const allowedTracking =
        localStorage.getItem('allowedTracking') === 'true';
      const userOnSite = localStorage.getItem('userOnSite') === 'true';

      dispatch(
        enterSite({
          site_id: siteId,
          idToken: idToken,
          allowed_tracking: allowedTracking,
          ack_status: acknowledgedAll,
          on_site: userOnSite,
          employee_id: employeeID,
        })
      ).then((response) => {
        if (response.meta.requestStatus === 'fulfilled') {
          console.log('Entered site successfully');
          const entryTime = response.payload.entry_time;
          dispatch(setEntryTime({ entryTime }));
          localStorage.setItem('entryTime', entryTime);
          router.push('/portal/jobs');
        } else {
          console.error('Failed to enter site');
        }
      });
    };

    if (!hasCompletedTraining && !accompaniedByEmployee) {
      dispatch(signOutUser()).then((response) => {
        console.log('Signing out...');
        if (response.meta.requestStatus === 'fulfilled') {
          console.log('Token revoked successfully');
        } else {
          console.log('Failed to revoke token');
        }
        localStorage.clear();
        router.push(`/login${siteId ? `?id=${siteId}` : ''}`);
      });
    } else {
      proceedAction();
    }
  };

  useEffect(() => {
    dispatch(
      getAcknowledgementDocuments({ site_id: siteId, idToken: idToken })
    ).then((response) => {
      if (response.meta.requestStatus === 'fulfilled') {
        console.log('Acknowledgement documents fetched successfully');
      } else {
        console.error('Failed to fetch acknowledgement documents');
      }
    });
  }, [dispatch]);

  return isLoading || !acknowledgementDocuments ? (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
      }}
    >
      <CircularProgress />
    </div>
  ) : (
    <Container
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        py: 4,
      }}
    >
      <NonNavbarLogo />
      <AcknowledgmentForm
        documents={acknowledgementDocuments}
        onProceed={handleProceed}
      />
    </Container>
  );
};

export default AcknowledgementPage;
