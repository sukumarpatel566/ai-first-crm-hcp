import { configureStore } from "@reduxjs/toolkit";
import interactionReducer from "./interactionSlice";

// Central Redux store for the HCP Interaction module.
export const store = configureStore({
  reducer: {
    interaction: interactionReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: [],
      },
    }),
});

// Verify store is created successfully
if (typeof window !== "undefined") {
  console.log("Redux store initialized:", store.getState());
}
