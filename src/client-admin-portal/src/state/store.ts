import { configureStore } from "@reduxjs/toolkit"
import userReducer from "./user/userSlice"
import documentReducer from "./document/documentSlice"
import siteReducer from "./site/siteSlice"
import siteVisitsReducer from './site/siteVisitsSlice';
import userManagementReducer from "./user/userManagementSlice"
import userRequestsReducer from "./user/userRequestsSlice"

export const store = configureStore({
    reducer: {
      user: userReducer,
      document: documentReducer,
      site: siteReducer,
      siteVisits: siteVisitsReducer,
      userManagement: userManagementReducer,
      userRequests: userRequestsReducer  // changed key here
    },
  });

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;