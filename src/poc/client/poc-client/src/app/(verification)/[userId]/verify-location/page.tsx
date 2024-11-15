'use client'
import React, { useState } from 'react'
import useSocket from '@/utils/hooks/useSocket';
import { useParams } from 'next/navigation';
import getGeolocation from '@/utils/getLocation';
import { verifyLocation } from '@/utils/wrapper';
import socket from '@/utils/socket';


const VerifyLocation = () => {
    const params = useParams<{ userId: string }>()
    const [isVerified, setIsVerified] = useState(false);
    const userId = params.userId;
    useSocket();
    const handleVerifyLocation = async () => {
        const { lat: lat, long: long } = await getGeolocation();
        try {
            let locationResponse  = await verifyLocation(userId, lat, long);
            setIsVerified(true)
        } catch (err) {
            console.log(err)
        }

        console.log(lat)
        console.log(long);
    }
    return (
        <>
            {isVerified ? <div>
                <p>Location Verified Successfully</p>
                <br />
                <p>You can close this page now</p>
            </div> :
                <div style={{ textAlign: "center" }}>
                    <button style={{ height: "50px", width: "auto", marginTop: "35vh", fontSize: "20px", padding: "5px" }} onClick={handleVerifyLocation}>Verify Location</button>

                    <p style={{ marginTop: "20px" }}>Please Click the above button to verify your location</p>
                </div>
            }
        </>
    );
}

export default VerifyLocation