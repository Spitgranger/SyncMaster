'use client'
import React, { useState } from 'react'
import useSocket from '@/utils/hooks/useSocket';
import { useParams } from 'next/navigation';
import getGeolocation from '@/utils/getLocation';
import { verifyLocation } from '@/utils/wrapper';
import socket from '@/utils/socket';


const VerifyLocation = () => {
    const params = useParams<{ userId: string }>()
    const [lat, setLat] = useState("0");
    const [long, setLong] = useState("0");
    const [isVerified, setIsVerified] = useState(false);
    const userId = params.userId;
    useSocket();
    socket.on('authSuccess', () => {
    })
    const handleVerifyLocation = async () => {
        // const { lat: lat, long: long } = await getGeolocation();
        let latitude = 43.25898815315478;
        let longitude = -79.92086378832343;
        try{
            await verifyLocation(userId, latitude, longitude);
            setIsVerified(true);
        }catch(err){
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
                    <p style={{ marginTop: "20px" }}>Latitude:{lat}</p>
                    <p style={{ marginTop: "20px" }}>Longitude:{long}</p>
                </div>
            }
        </>
    );
}

export default VerifyLocation