import React from 'react'

const Dashboard: React.FC<{ params: { userId: string } }> = ({ params }) => {
    const { userId } = params;
    return (
        <>
            <div>Dashboard</div>
            <div>User ID = {userId}</div>
        </>
    )
}

export default Dashboard