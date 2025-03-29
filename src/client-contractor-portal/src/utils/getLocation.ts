const getGeolocation = async (): Promise<[number | null, number | null]> => {
    try {
        const pos: GeolocationPosition = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve as PositionCallback, reject);
        });
        return [pos.coords.latitude, pos.coords.longitude];
    } catch (error) {
        console.log('Error getting geolocation:', error);
        return [null, null];
    }
}

export default getGeolocation;