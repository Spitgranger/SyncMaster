import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

interface Attachment {
  name: string;
  url: string;
}

interface SiteVisit {
  site_id: string;
  user_id: string;
  user_email: string;
  entry_time: string;
  allowed_tracking: boolean;
  ack_status: boolean;
  exit_time: string;
  work_order: number;
  description: string;
  on_site: boolean;
  employee_id: string;
  attachments: Attachment[];
}

export interface GetSiteVisitsParams {
  from_time?: string;
  to_time?: string;
  limit?: number;
  start_key?: string;
}

export interface FetchSiteVisitsArgs {
  params: GetSiteVisitsParams;
  idToken: string;
}

interface SiteVisitsResponse {
  visits: SiteVisit[];
  last_key: string;
}

interface SiteVisitsState {
  visits: SiteVisit[];
  lastKey: string | null;
  isLoading: boolean;
}

const initialState: SiteVisitsState = {
  visits: [],
  lastKey: null,
  isLoading: false,
};

export const getSiteVisits = createAsyncThunk<
  SiteVisitsResponse,
  FetchSiteVisitsArgs,
  { rejectValue: string }
>(
  'siteVisits/getSiteVisits',
  async ({ params, idToken }, { rejectWithValue }) => {
    try {
      const url = new URL(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/visits`);

      // Append allowed query parameters only
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Authorization': idToken,
          'Content-Type': 'application/json'
        },
      });

      if (!response.ok) {
        const errorMessage = await response.text();
        return rejectWithValue(errorMessage);
      }

      const data: SiteVisitsResponse = await response.json();
      return data;
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

const siteVisitsSlice = createSlice({
  name: 'siteVisits',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getSiteVisits.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getSiteVisits.fulfilled, (state, action) => {
        state.isLoading = false;
        state.visits = action.payload.visits;
        state.lastKey = action.payload.last_key;
      })
      .addCase(getSiteVisits.rejected, (state) => {
        state.isLoading = false;
      });
  },
});

export default siteVisitsSlice.reducer;
