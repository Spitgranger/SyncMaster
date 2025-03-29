import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { create } from 'domain';

interface SiteState {
    entryTime: string | null;
    isEnteringOrExitingSite: boolean;
}

const initialState: SiteState = {
    entryTime: "",
    isEnteringOrExitingSite: false,
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
    extraReducers: (builder) => {
        builder
            .addCase(enterSite.pending, (state) => {
                state.isEnteringOrExitingSite = true;
            }
            )
            .addCase(enterSite.fulfilled, (state) => {
                state.isEnteringOrExitingSite = false;
            }
            )
            .addCase(enterSite.rejected, (state) => {
                state.isEnteringOrExitingSite = false;
            });
    }
});

export const enterSite = createAsyncThunk(
    'site/enterSite',
    async ({ site_id, idToken, allowed_tracking, ack_status, on_site, employee_id }:
        {
            site_id: string | undefined, idToken: string | null, allowed_tracking: boolean,
            ack_status: boolean, on_site: boolean, employee_id: string | null
        }) => {

        let requestBody = null;

        if (employee_id !== null) {
            requestBody = {
                allowed_tracking: allowed_tracking,
                ack_status: ack_status,
                on_site: on_site,
                employee_id: employee_id,
            }
        } else {
            requestBody = {
                allowed_tracking: allowed_tracking,
                ack_status: ack_status,
                on_site: on_site,
            }
        }

        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/enter`, {
            method: 'POST',
            headers: {
                "Content-Type": 'application/json',
                "Authorization": `${idToken}`,
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            throw new Error('Failed to enter site');
        }
        return response.json();
    })
export const { setEntryTime, clearEntryTime } = siteSlice.actions;

export default siteSlice.reducer;