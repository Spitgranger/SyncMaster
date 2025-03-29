import { configureStore } from "@reduxjs/toolkit"
import userReducer from "./user/userSlice"
import documentReducer from "./document/documentSlice"
import siteReducer from "./site/siteSlice"

export const store = configureStore({
    reducer: {
        user: userReducer,
        document: documentReducer,
        site: siteReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;