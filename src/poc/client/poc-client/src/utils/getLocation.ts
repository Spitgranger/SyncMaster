const getGeolocation = async (): Promise<{ long: number, lat: number }> => {
    try {
        const pos: GeolocationPosition = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve as PositionCallback, reject);
        });
        return { long: pos.coords.longitude, lat: pos.coords.latitude, };
    } catch (error) {
        console.log('Error getting geolocation:', error);
        return { long: null, lat: null, };
    }
}

export default getGeolocation;