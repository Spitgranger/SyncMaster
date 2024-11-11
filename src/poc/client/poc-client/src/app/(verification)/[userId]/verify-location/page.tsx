import React from 'react'

const VerifyLocation: React.FC<{ params: { userId: string } }> = ({ params }) => {
    const { userId } = params;
    return (
        <>
            <div>Verify Location</div> <div>User ID = {userId}</div>

        </>
    );
}

export default VerifyLocation