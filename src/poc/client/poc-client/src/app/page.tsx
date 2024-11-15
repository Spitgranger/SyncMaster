'use client'
import React, { useEffect, useState } from 'react';
import Landing from '@/components/Landing/Landing';
import getGeolocation from '@/utils/getLocation';
import { useRouter } from 'next/navigation';
import { createSession, verifyLocation } from '@/utils/wrapper';

const LandingPage: React.FC = () => {

  const router = useRouter();
  const [userId, setUserId] = useState<string>("null");

  useEffect(() => {
    async function fetchUserId() {
      let response = await createSession();
      setUserId(response.uuid);
    }
    fetchUserId();
  }, [])

  const handlePortalClick = async () => {
    const { lat: lat, long: long } = await getGeolocation();
    console.log(lat)
    console.log(long);

    if (lat === null || long === null) {
      router.push(`/${userId}/qr-code`)
    } else {
      //create session
      //send location for verification
      try {
        const locationVerified = await verifyLocation(userId, lat, long);
        console.log(locationVerified);
        router.push('/portal');
      } catch (err) {
        console.log(err);
        router.push(`/${userId}/qr-code`)

      }
    }
  };
  return (
    <Landing onClick={handlePortalClick} />
  );
};

export default LandingPage;
