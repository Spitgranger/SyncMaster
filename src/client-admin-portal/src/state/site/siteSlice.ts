import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface SiteState {
    // Define the state structure here
    sites: any[],
    isLoadingSites: boolean
}

const initialState: SiteState = {
    sites: [],
    isLoadingSites: false
};

const siteSlice = createSlice({
    name: 'site',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(getSites.pending, (state) => {
                state.isLoadingSites = true;
            })
            .addCase(getSites.fulfilled, (state, action) => {
                state.sites = action.payload.sites;
                state.isLoadingSites = false;
            })
            .addCase(getSites.rejected, (state) => {
                state.isLoadingSites = false;
            });
    }
});


export const getSites = createAsyncThunk(
    "site/getSites",
    async (payload: any) => {
        const { idToken } = payload;
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site-management`, {
            method: "GET",
            headers: {
                "Authorization": `${idToken}`,
                "Content-Type": "application/json"
            }
        })
        if (response.ok) {
            return response.json()
        } else {
            throw new Error("Failed to fetch sites")
        }
    }
)

export const deleteSite = createAsyncThunk(
    "site/deleteSite",
    async (payload: any) => {
        const { site_id, idToken } = payload;
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site-management/${site_id}`, {
            method: "DELETE",
            headers: {
                "Authorization": `${idToken}`,
                "Content-Type": "application/json"
            }
        })
        if (!response.ok) {
            throw new Error("Failed to delete site")
        }
        return true;
})

export const createSite = createAsyncThunk(
    "site/createSite",
    async (payload: any) => {
        const { site_id, longitude, latitude, acceptable_range,idToken } = payload;
        console.log(payload);
        
        const requestBody = {
            site_id: site_id,
            longitude: longitude,
            latitude: latitude,
            acceptable_range: acceptable_range
        }
        const requetJson = JSON.stringify(requestBody)
        console.log("request body here", requetJson);
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site-management`, {
            method: "POST",
            headers: {
                "Authorization": `${idToken}`,
                "Content-Type": "application/json"
            },
            body: requetJson
        })
        if (!response.ok) {
            throw new Error("Failed to create site")
        }
        return true;
    }
)


export const updateSite = createAsyncThunk(
    "site/updateSite",
    async (payload: any) => {
        const { site_id, longitude, latitude, acceptable_range, idToken } = payload;
        const requestBody = {
            latitude: latitude,
            longitude: longitude,
            acceptable_range: acceptable_range
        }
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site-management/${site_id}`, {
            method: "PATCH",
            headers: {
                "Authorization": `${idToken}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        })
        if (!response.ok) {
            throw new Error("Failed to update site")
        }
        return true;
    }
)


export default siteSlice.reducer;