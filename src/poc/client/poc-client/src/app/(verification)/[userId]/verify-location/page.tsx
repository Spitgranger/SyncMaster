import React from 'react'
import useSocket from '../../../../utils/hooks/useSocket.ts'

const VerifyLocation: React.FC<{ params: { userId: string } }> = ({params}) => {
    const {userId} = params;
    useSocket();
    return (
        <>
            <div>Verify Location</div>
            <div>User ID = {userId}</div>

        </>
    );
}

export default VerifyLocation