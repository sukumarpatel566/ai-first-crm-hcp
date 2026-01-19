import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

// Async thunks for calling backend APIs
export const createStructuredInteraction = createAsyncThunk(
  "interaction/createStructured",
  async (payload, { rejectWithValue }) => {
    try {
      const res = await axios.post(`${API_BASE}/interactions/structured`, payload);
      return res.data;
    } catch (err) {
      return rejectWithValue(err.response?.data || { detail: "Error creating interaction" });
    }
  }
);

export const createChatInteraction = createAsyncThunk(
  "interaction/createChat",
  async (payload, { rejectWithValue }) => {
    try {
      const res = await axios.post(
        `${API_BASE}/interactions/chat`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      
      // Ensure we have a valid response
      if (res.status >= 200 && res.status < 300) {
        return res.data;
      } else {
        return rejectWithValue({
          detail: `Unexpected status: ${res.status}`,
        });
      }
    } catch (err) {
      // Extract error message from response
      const errorMessage = err.response?.data?.detail || 
                           err.response?.data?.message ||
                           err.message ||
                           "Error creating chat interaction";
      
      console.error("Chat interaction error:", {
        status: err.response?.status,
        data: err.response?.data,
        message: errorMessage,
      });
      
      return rejectWithValue({
        detail: errorMessage,
      });
    }
  }
);

const interactionSlice = createSlice({
  name: "interaction",
  initialState: {
    mode: "form", // "form" | "chat"
    loading: false,
    error: null,
    lastInteraction: null,
    chatToolResult: null,
  },
  reducers: {
    setMode(state, action) {
      state.mode = action.payload;
    },
    clearError(state) {
      state.error = null;
    },
    clearChatResult(state) {
      state.chatToolResult = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createStructuredInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createStructuredInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.lastInteraction = action.payload;
      })
      .addCase(createStructuredInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.detail || "Failed to save interaction";
      })
      .addCase(createChatInteraction.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createChatInteraction.fulfilled, (state, action) => {
        state.loading = false;
        state.chatToolResult = action.payload;
      })
      .addCase(createChatInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.detail || "Failed to process chat interaction";
      });
  },
});

export const { setMode, clearError, clearChatResult } = interactionSlice.actions;
export default interactionSlice.reducer;

