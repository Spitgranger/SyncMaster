import React, { useState } from 'react';
import { createSession, verifyLocation, emitConnection } from '../../app/(api)/_utils/wrapper';

const WrapperTestComponent: React.FC = () => {
  const [sessionId, setSessionId] = useState<string>("null");
  const [verificationResult, setVerificationResult] = useState<string>("null");
  const [emitConnectionResult, setEmitConnectionResult] = useState<string>("null");
  const [locationData, setLocationData] = useState({ latitude: 0, longitude: 0 });

  const createSessionPress = async () => {
    const response = await createSession();
    setSessionId(response.uuid);
    console.log(sessionId)
  };

  const verifyLocationPress = async () => {
    const response = await verifyLocation(sessionId, locationData.latitude, locationData.longitude);
    setVerificationResult(response.message);
    console.log(verificationResult)
  };

  const emitConnectionPress = async () => {
    const response = await emitConnection(sessionId);
    setEmitConnectionResult(response.message);
    console.log(emitConnectionResult)
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
          onChange={(e) => setLocationData({ ...locationData, latitude: parseFloat(e.target.value) })}
        />
        <input
          type="number"
          placeholder="Longitude"
          value={locationData.longitude}
          onChange={(e) => setLocationData({ ...locationData, longitude: parseFloat(e.target.value) })}
        />
        <button onClick={verifyLocationPress}>Verify Location</button>
      </div>

      <button onClick={emitConnectionPress}>Emit Connection</button>
    </div>
  );
};

export default WrapperTestComponent;
