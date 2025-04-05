const getGeolocation = async (): Promise<number[]> => {
  try {
    const pos: GeolocationPosition = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        resolve as PositionCallback,
        reject
      );
    });
    return [pos.coords.latitude, pos.coords.longitude];
  } catch (error) {
    console.log('Error getting geolocation:', error);
    return [0, 0];
  }
};

export default getGeolocation;
