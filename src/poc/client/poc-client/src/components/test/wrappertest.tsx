import React, { useState } from 'react';
import { createSession, verifyLocation, emitConnection } from '../../app/(api)/_utils/wrapper';

const WrapperTestComponent: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [verificationResult, setVerificationResult] = useState<string | null>(null);
  const [locationData, setLocationData] = useState({ latitude: 0, longitude: 0 });

  const handleCreateSession = async () => {
    try {
      const response = await createSession();
      setSessionId(response.uuid);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const handleVerifyLocation = async () => {
    if (!sessionId) {
      console.log('Create a session first');
      return;
    }

    try {
      const response = await verifyLocation(sessionId, locationData.latitude, locationData.longitude);
      setVerificationResult(response.message);
    } catch (error) {
      console.error('Error verifying location:', error);
    }
  };

  const handleEmitConnection = () => {
    try {
      if (!sessionId) {
        console.log('Create a session first');
        return;
      }
      emitConnection(sessionId);
      console.log('Connection event emitted');
    } catch (error) {
      console.error('Error emitting connection:', error);
    }
  };

  return (
    <div>
      <h2>API Wrapper Test</h2>

      <button onClick={handleCreateSession}>Create Session</button>
      {sessionId && <p>Session ID: {sessionId}</p>}

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
        <button onClick={handleVerifyLocation}>Verify Location</button>
        {verificationResult && <p>Verification Result: {verificationResult}</p>}
      </div>

      <button onClick={handleEmitConnection}>Emit Connection</button>
    </div>
  );
};

export default WrapperTestComponent;
