import React, {useState} from 'react';
import {createSession, verifyLocation, emitConnection} from '../../utils/wrapper';
import useSocket from "@/utils/hooks/useSocket";
import socket from "@/utils/socket";

const WrapperTestComponent: React.FC = () => {
    const [sessionId, setSessionId] = useState<string>("null");
    const [locationData, setLocationData] = useState({latitude: 0, longitude: 0});
    useSocket();
    const createSessionPress = async () => {
        try {
            const response = await createSession();
            setSessionId(response.uuid);
            socket.emit("join_session", response.uuid);
            console.log(socket)
            console.log(response.uuid)
        } catch (error) {
            console.log(error)
        }
    };

    const verifyLocationPress = async () => {
        try {
            const response = await verifyLocation(sessionId, locationData.latitude, locationData.longitude);
            console.log(response.message)
        } catch (error) {
            console.log(error)
        }
    };

    const emitConnectionPress = async () => {
        try {
            const response = await emitConnection(sessionId);
            console.log(response.message)
        } catch (error) {
            console.log(error)
        }
    };

    const longitudeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        try {
            if (isNaN(parseFloat(e.target.value))) {
                throw new Error('An error occurred');
            }
            setLocationData({...locationData, longitude: parseFloat(e.target.value)})
        } catch (error) {
            console.log(error)
        }
    };

    const latitudeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        try {
            if (isNaN(parseFloat(e.target.value))) {
                throw new Error('An error occurred');
            }
            setLocationData({...locationData, latitude: parseFloat(e.target.value)})
        } catch (error) {
            console.log(error)
        }
    };

    return (
        <div>
            <h2>API Wrapper Test</h2>
            <button onClick={createSessionPress}>Create Session</button>
            <div>
                <h3>Verify Location</h3>
                <input
                    type="number"
                    placeholder="Latitude"
                    value={locationData.latitude}
                    onChange={latitudeChange}
                />
                <input
                    type="number"
                    placeholder="Longitude"
                    value={locationData.longitude}
                    onChange={longitudeChange}
                />
                <button onClick={verifyLocationPress}>Verify Location</button>
            </div>

            <button onClick={emitConnectionPress}>Emit Connection</button>
        </div>
    );
};

export default WrapperTestComponent;
