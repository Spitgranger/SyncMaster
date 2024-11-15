'use client'
import React, { useState } from 'react'

import { useParams } from 'next/navigation';
import useSocket from '@/utils/hooks/useSocket';
import socket from '@/utils/socket';
import QRCode from 'react-qr-code';
import { useRouter } from 'next/navigation';

const QrCode = () => {
    const router = useRouter()
    const params = useParams<{ userId: string }>()
    const userId = params.userId;
    const isLocationVerified = useState(false);
    useSocket()
    socket.emit("join_session", userId);
    socket.on('authSuccess', () => {
        router.push('/portal')
    })
    return (
        <>
            <div style={{ height: "auto", margin: "30vh auto", maxWidth: 256, width: "100%" }}>
                <QRCode
                    size={256}
                    style={{ height: "auto", maxWidth: "100%", width: "100%" }}
                    value={`${process.env.NEXT_PUBLIC_ADDRESS}:3000/${userId}/verify-location`}
                    viewBox={`0 0 256 256`}
                />
                <p style={{ marginTop: "20px" }}>Please scan the QR code using your phone to verify your location</p>
            </div>


        </>
    );
}

export default QrCode