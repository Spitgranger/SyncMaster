import React, { useState } from 'react';
//import { createSession, verifyLocation, emitConnection } from '../../app/(api)/_utils/wrapper';

const WrapperTestComponent: React.FC = () => {
  //const [sessionId, setSessionId] = useState<string | null>(null);
  //const [verificationResult, setVerificationResult] = useState<string | null>(null);
  const [locationData, setLocationData] = useState({ latitude: 0, longitude: 0 });

  const doNothing = async () => {
  };

  return (
    <div>
      <h2>API Wrapper Test</h2>
      <button onClick={doNothing}>Create Session</button>
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
        <button onClick={doNothing}>Verify Location</button>
      </div>

      <button onClick={doNothing}>Emit Connection</button>
    </div>
  );
};

export default WrapperTestComponent;
