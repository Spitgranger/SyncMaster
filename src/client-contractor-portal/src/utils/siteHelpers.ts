export const getEntryTimeFromLocalStorage = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('entryTime');
    }
    return null;
};