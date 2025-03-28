import { createSlice } from '@reduxjs/toolkit';
import { getEntryTime } from '@/utils/siteHelpers';

interface SiteState {
    entryTime: string | null;
}

const initialState: SiteState = {
    entryTime: getEntryTime(),
};

const siteSlice = createSlice({
    name: 'site',
    initialState,
    reducers: {
        setEntryTime(state, action) {
            state.entryTime = action.payload;
            localStorage.setItem('entryTime', action.payload);
        },
        clearEntryTime(state) {
            state.entryTime = null;
            localStorage.removeItem('entryTime');
        },
    },
});

export const { setEntryTime, clearEntryTime } = siteSlice.actions;

export default siteSlice.reducer;