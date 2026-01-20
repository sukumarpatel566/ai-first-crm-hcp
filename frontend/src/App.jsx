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
  const { error = null } = useSelector((state) => state?.interaction || {});

  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        background: "#f5f7fa",
        fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto", padding: "24px 20px" }}>
        {/* Page Title */}
        <h1
          style={{
            fontSize: 24,
            fontWeight: 600,
            color: "#1e293b",
            marginBottom: 24,
            letterSpacing: "-0.02em",
          }}
        >
          Log HCP Interaction
        </h1>

        {error && (
          <div
            style={{
              marginBottom: 16,
              padding: "12px 16px",
              borderRadius: 8,
              backgroundColor: "#fef2f2",
              color: "#991b1b",
              fontSize: 14,
              border: "1px solid #fecaca",
            }}
          >
            {typeof error === "string" ? error : error?.detail || "An error occurred"}
          </div>
        )}

        {/* Two-Column Layout */}
        <div
          style={{
            display: "flex",
            gap: 20,
            alignItems: "flex-start",
          }}
        >
          {/* Left Panel - Form (70%) */}
          <div style={{ flex: "0 0 70%", minWidth: 0 }}>
            <LogInteractionForm />
          </div>

          {/* Right Panel - AI Assistant (30%) */}
          <div style={{ flex: "0 0 30%", minWidth: 0 }}>
            <LogInteractionChat />
          </div>
        </div>
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

