import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '@/state/store';

interface UserManagementState {
  users: any[]; // Ideally, change "any" to a more specific type.
  loading: boolean;
  error: string | null;
  createUserStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
  updateUserStatus: 'idle' | 'loading' | 'succeeded' | 'failed';
}

const initialState: UserManagementState = {
  users: [],
  loading: false,
  error: null,
  createUserStatus: 'idle',
  updateUserStatus: 'idle',
};

export const createUser = createAsyncThunk(
  'userManagement/createUser',
  async (
    userData: {
      email: string;
      attributes: {
        "custom:role": "admin" | "contractor" | "employee";
        "custom:company": string;
        name: string;
      };
    },
    thunkAPI
  ) => {
    if (!["admin", "contractor", "employee"].includes(userData.attributes["custom:role"])) {
      throw new Error("Invalid role provided");
    }
    const state = thunkAPI.getState() as RootState;
    const idToken = state.user.idToken;
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/users/create_user`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": idToken || ""
      },
      body: JSON.stringify(userData),
    });
    if (response.ok) {
      return response.json();
    }
    throw new Error("Failed to create user");
  }
);

export const getUsers = createAsyncThunk(
  'userManagement/getUsers',
  async (attributes: Record<string, any>, thunkAPI) => {
    const state = thunkAPI.getState() as RootState;
    const idToken = state.user.idToken;
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/users/get_users`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": idToken || ""
      },
      body: JSON.stringify({ attributes }),
    });
    if (response.ok) {
      return response.json();
    }
    throw new Error("Failed to fetch users");
  }
);

export const updateUser = createAsyncThunk(
    'userManagement/updateUser',
    async (
      updateData: {
        email: string;
        attributes: {
          "custom:role": "admin" | "contractor" | "employee";
          "custom:company": string;
          name: string;
        };
      },
      thunkAPI
    ) => {
      const state = thunkAPI.getState() as RootState;
      const idToken = state.user.idToken;
  
      const attributesArray = [
        { Name: "name", Value: updateData.attributes.name },
        { Name: "custom:company", Value: updateData.attributes["custom:company"] },
        { Name: "custom:role", Value: updateData.attributes["custom:role"] }
      ];
  
      const payload = {
        email: updateData.email,
        attributes: attributesArray,
      };
  
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/users/update_user`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": idToken || ""
        },
        body: JSON.stringify(payload),
      });
  
      if (response.ok) {
        const text = await response.text();
        return text ? JSON.parse(text) : {};
      }
      throw new Error("Failed to update user");
    }
  );
  

const userManagementSlice = createSlice({
  name: 'userManagement',
  initialState,
  reducers: {
    resetCreateUserStatus: (state) => {
      state.createUserStatus = 'idle';
    },
  },
  extraReducers: (builder) => {
    // createUser
    builder.addCase(createUser.pending, (state) => {
      state.createUserStatus = 'loading';
      state.error = null;
    });
    builder.addCase(createUser.fulfilled, (state, action: PayloadAction<any>) => {
      state.createUserStatus = 'succeeded';
      state.users.push(action.payload);
    });
    builder.addCase(createUser.rejected, (state, action) => {
      state.createUserStatus = 'failed';
      state.error = action.error.message || 'Failed to create user';
    });
    // getUsers
    builder.addCase(getUsers.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(getUsers.fulfilled, (state, action: PayloadAction<any[]>) => {
      state.loading = false;
      state.users = action.payload;
    });
    builder.addCase(getUsers.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch users';
    });
    // updateUser
    builder.addCase(updateUser.pending, (state) => {
      state.updateUserStatus = 'loading';
      state.error = null;
    });
    builder.addCase(updateUser.fulfilled, (state, action: PayloadAction<any>) => {
      state.updateUserStatus = 'succeeded';
      const updatedUser = action.payload;
      const index = state.users.findIndex(user => user.email === updatedUser.email);
      if (index !== -1) {
        state.users[index] = updatedUser;
      }
    });
    builder.addCase(updateUser.rejected, (state, action) => {
      state.updateUserStatus = 'failed';
      state.error = action.error.message || 'Failed to update user';
    });
  },
});

export const { resetCreateUserStatus } = userManagementSlice.actions;
export default userManagementSlice.reducer;
