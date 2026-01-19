import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { setMode, clearError } from "./redux/interactionSlice";
import LogInteractionForm from "./components/LogInteractionForm";
import LogInteractionChat from "./components/LogInteractionChat";

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "Inter, sans-serif",
            padding: "20px",
          }}
        >
          <div style={{ maxWidth: 600, textAlign: "center" }}>
            <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 16 }}>
              Something went wrong
            </h1>
            <p style={{ color: "#6b7280", marginBottom: 16 }}>
              {this.state.error?.message || "An unexpected error occurred"}
            </p>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: "10px 20px",
                borderRadius: 8,
                border: "none",
                background: "#2563eb",
                color: "white",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const App = () => {
  console.log("App rendered");
  
  // Hooks must be called unconditionally
  const dispatch = useDispatch();
  const { mode = "form", error = null } = useSelector((state) => state?.interaction || {});

  const toggleMode = (newMode) => {
    dispatch(setMode(newMode));
    dispatch(clearError());
  };

  // Ensure we always return visible content
  if (!mode) {
    console.warn("Mode is undefined, defaulting to 'form'");
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "radial-gradient(circle at top left, #eef2ff, #f9fafb)",
        fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "32px 16px 48px" }}>
        <header style={{ marginBottom: 32 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <h1 style={{ fontSize: 28, fontWeight: 700, letterSpacing: -0.03 }}>
                AI-First CRM – HCP Interaction Log
              </h1>
              <p style={{ marginTop: 8, color: "#6b7280", fontSize: 14, maxWidth: 560 }}>
                Capture Healthcare Professional interactions either via a structured form
                or conversationally. The AI agent structures notes, extracts entities,
                and recommends next best actions in your CRM workflow.
              </p>
            </div>
            <span
              style={{
                fontSize: 12,
                padding: "4px 10px",
                borderRadius: 999,
                backgroundColor: "#e0f2fe",
                color: "#0369a1",
                border: "1px solid #bae6fd",
              }}
            >
              Powered by LangGraph + Groq (gemma2-9b-it)
            </span>
          </div>
        </header>

        <div
          style={{
            display: "inline-flex",
            borderRadius: 999,
            padding: 3,
            backgroundColor: "#e5e7eb",
            marginBottom: 20,
          }}
        >
          <button
            type="button"
            onClick={() => toggleMode("form")}
            style={{
              padding: "6px 16px",
              borderRadius: 999,
              border: "none",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              backgroundColor: mode === "form" ? "#ffffff" : "transparent",
              boxShadow: mode === "form" ? "0 6px 18px rgba(15,23,42,0.10)" : "none",
            }}
          >
            Structured Form
          </button>
          <button
            type="button"
            onClick={() => toggleMode("chat")}
            style={{
              padding: "6px 16px",
              borderRadius: 999,
              border: "none",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              backgroundColor: mode === "chat" ? "#ffffff" : "transparent",
              boxShadow: mode === "chat" ? "0 6px 18px rgba(15,23,42,0.10)" : "none",
            }}
          >
            Conversational Chat
          </button>
        </div>

        {error && (
          <div
            style={{
              marginBottom: 16,
              padding: "10px 14px",
              borderRadius: 12,
              backgroundColor: "#fef2f2",
              color: "#991b1b",
              fontSize: 13,
              border: "1px solid #fecaca",
            }}
          >
            {error}
          </div>
        )}

        {mode === "form" ? <LogInteractionForm /> : <LogInteractionChat />}
      </div>
    </div>
  );
};

// Wrap App with ErrorBoundary
const AppWithErrorBoundary = () => (
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);

export default AppWithErrorBoundary;

