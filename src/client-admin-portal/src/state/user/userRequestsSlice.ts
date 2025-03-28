import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '@/state/store';

interface UserRequest {
  email: string;
  // add other fields returned by your get-requests endpoint if needed
}

interface UserRequestsState {
  requests: UserRequest[];
  loading: boolean;
  error: string | null;
  actionRequestStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
}

const initialState: UserRequestsState = {
  requests: [],
  loading: false,
  error: null,
  actionRequestStatus: 'idle',
};

// GET /protected/user-requests/get-requests?limit=...&start_key=...
export const getUserRequests = createAsyncThunk(
  'userRequests/getUserRequests',
  async (
    params: { limit?: number; start_key?: string },
    thunkAPI
  ) => {
    const state = thunkAPI.getState() as RootState;
    const idToken = state.user.idToken;
    const queryParams = new URLSearchParams();
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params.start_key) queryParams.append('start_key', params.start_key);
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/user-requests/get-requests?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': idToken || ''
      },
    });
    if (response.ok) {
      return response.json();
    }
    throw new Error("Failed to get user requests");
  }
);

// POST /protected/user-requests/action-request
// Expected payload: { "email": "user@example.com", "action": "accept" or "reject" }
export const actionRequest = createAsyncThunk(
  'userRequests/actionRequest',
  async (
    data: { email: string; action: "accept" | "reject" },
    thunkAPI
  ) => {
    const state = thunkAPI.getState() as RootState;
    const idToken = state.user.idToken;
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/user-requests/action-request`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': idToken || ''
      },
      body: JSON.stringify(data),
    });
    if (response.ok) {
      return response.json();
    }
    throw new Error("Failed to perform action on user request");
  }
);

const userRequestsSlice = createSlice({
  name: 'userRequests',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    // getUserRequests cases
    builder.addCase(getUserRequests.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(getUserRequests.fulfilled, (state, action: PayloadAction<UserRequest[]>) => {
      state.loading = false;
      state.requests = action.payload;
    });
    builder.addCase(getUserRequests.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to get user requests';
    });

    // actionRequest cases
    builder.addCase(actionRequest.pending, (state) => {
      state.actionRequestStatus = 'loading';
      state.error = null;
    });
    builder.addCase(actionRequest.fulfilled, (state, action: PayloadAction<any>) => {
      state.actionRequestStatus = 'succeeded';
      // Optionally update or remove the request from state.requests if needed.
    });
    builder.addCase(actionRequest.rejected, (state, action) => {
      state.actionRequestStatus = 'failed';
      state.error = action.error.message || 'Failed to perform action on user request';
    });
  },
});

export default userRequestsSlice.reducer;
