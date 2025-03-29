import { initializeUser } from "@/utils/userHelpers";
import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import router  from "next/router";
import jwt from 'jsonwebtoken'

interface UserState {
    accessToken: string | null;
    idToken: string | null;
    isSignedIn: boolean;
    role: string | null;
    username: string | null;
    userId: string | null;
}

const initialState: UserState = initializeUser()

const userSlice = createSlice({
    name: "user",
    initialState,
    reducers: {
        signIn: (state, action) => {

        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(signInUser.fulfilled, (state, action) => {
                const accessToken = action.payload.AccessToken
                const idToken = action.payload.IdToken
                const decodedToken: any = jwt.decode(idToken);
                state.accessToken = accessToken
                state.idToken = idToken
                state.isSignedIn = true
                state.role = decodedToken["custom:role"];
                state.username = decodedToken["name"]
                state.userId = decodedToken["sub"]
            })
            .addCase(signOutUser.fulfilled, (state) => {
                state.accessToken = null
                state.idToken = null
                state.isSignedIn = false
                state.role = null
                state.username = null
                console.log(state);
            }
            )
    }
})

export const signInUser = createAsyncThunk(
  "user/signIn",
  async (userData: any) => {
    const { email, password, new_password } = userData;
    const body = {
      email,
      password,
      ...(new_password ? { new_password } : {})
    };

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/unprotected/auth/signin`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (response.ok) {
      return response.json();
    } else if (response.status === 403) {
      // Redirect to reset-password page for OTP scenario
      router.push("/reset-password");
      // Throwing an error to update the thunk lifecycle (optional)
      throw new Error("OTP detected: redirecting to reset-password page.");
    } else if (response.status === 404) {
      // Throwing an error to update the thunk lifecycle (optional)
      throw new Error("User not found");
    } else if (response.status === 401) {
      // Throwing an error to update the thunk lifecycle (optional)
      throw new Error("Incorrect password");
    } else {
      throw new Error("Failed to Sign In");
    }
  }
);

export const signOutUser = createAsyncThunk(
    "user/signOut",
    // userToken: string, IdToken: string
    async (_, thunkAPI) => {
        const state = thunkAPI.getState() as { user: UserState }
        const userData = state.user
        console.log(userData);
        
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/users/signout?user_token=${userData.accessToken}`, {
            method: "GET",
            headers: {
                "Authorization": `${userData.idToken}`,
                "Content-Type": "application/json"
            },
        });
        if (!response.ok) {
            throw new Error("Failed to sign out");
        }
        return true;
    }
)

export default userSlice.reducer