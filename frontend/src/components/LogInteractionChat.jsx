import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createChatInteraction, clearChatResult } from "../redux/interactionSlice";

const Card = ({ children }) => (
  <div
    style={{
      backgroundColor: "#ffffff",
      borderRadius: 12,
      padding: 24,
      boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
      border: "1px solid #e2e8f0",
    }}
  >
    {children}
  </div>
);

export const LogInteractionChat = () => {
  const dispatch = useDispatch();
  const { loading = false, chatToolResult = null } = useSelector((state) => state?.interaction || {});

  const [freeText, setFreeText] = useState("");
  const [channel, setChannel] = useState("In-Person");

  const handleSubmit = (e) => {
    e.preventDefault();
    dispatch(
      createChatInteraction({
        free_text: freeText,
        channel,
      })
    );
  };

  const handleClear = () => {
    setFreeText("");
    dispatch(clearChatResult());
  };

  const tool = chatToolResult?.tool_result || {};

  return (
    <Card>
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>
        Conversational Log (AI Assisted)
      </h2>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label style={{ fontWeight: 500 }}>Channel</label>
          <select
            value={channel}
            onChange={(e) => setChannel(e.target.value)}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1" }}
          >
            <option>In-Person</option>
            <option>Call</option>
            <option>Virtual</option>
          </select>
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label style={{ fontWeight: 500 }}>Describe the interaction</label>
          <textarea
            rows={6}
            value={freeText}
            onChange={(e) => setFreeText(e.target.value)}
            placeholder="Example: Met Dr. Smith to discuss Product A, she was interested but requested real-world data..."
            style={{
              padding: 10,
              borderRadius: 8,
              border: "1px solid #cbd5f1",
              resize: "vertical",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !freeText.trim()}
          style={{
            marginTop: 8,
            padding: "10px 16px",
            borderRadius: 999,
            border: "none",
            background: loading ? "#cbd5f1" : "linear-gradient(90deg,#2563eb,#4f46e5)",
            color: "white",
            fontWeight: 600,
            cursor: loading || !freeText.trim() ? "default" : "pointer",
          }}
        >
          {loading ? "Processing..." : "Let AI Structure It"}
        </button>
      </form>

      {tool.interaction_id && (
        <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid #e2e8f0" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 8,
            }}
          >
            <h3 style={{ fontSize: 16, fontWeight: 600 }}>AI Extracted Summary</h3>
            <button
              type="button"
              onClick={handleClear}
              style={{
                border: "none",
                background: "transparent",
                color: "#64748b",
                fontSize: 13,
                cursor: "pointer",
              }}
            >
              Clear
            </button>
          </div>

          <p style={{ fontSize: 14, color: "#4b5563", marginBottom: 12 }}>
            {tool.summary || "No summary available."}
          </p>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
              gap: 12,
              fontSize: 13,
              color: "#475569",
            }}
          >
            <div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>HCP</div>
              <div>{tool.hcp_name}</div>
              <div style={{ color: "#6b7280" }}>{tool.specialty}</div>
            </div>
            <div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Products Discussed</div>
              <div>{tool.products_discussed || "N/A"}</div>
            </div>
            <div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Sentiment</div>
              <span
                style={{
                  padding: "2px 8px",
                  borderRadius: 999,
                  backgroundColor: "#eff6ff",
                  color: "#1d4ed8",
                }}
              >
                {tool.sentiment || "N/A"}
              </span>
            </div>
            <div>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Follow-up Action</div>
              <div>{tool.follow_up_action || "N/A"}</div>
            </div>
          </div>

          <p
            style={{
              marginTop: 16,
              fontSize: 12,
              color: "#6b7280",
            }}
          >
            Review the extracted details above in your CRM context before treating this
            as final. This module shows a confirmation view; persistence is already
            handled server-side.
          </p>
        </div>
      )}
    </Card>
  );
};

export default LogInteractionChat;

