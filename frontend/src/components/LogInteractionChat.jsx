import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createChatInteraction, clearChatResult } from "../redux/interactionSlice";

// Card container component
const Card = ({ children, style = {} }) => (
  <div
    style={{
      backgroundColor: "#ffffff",
      borderRadius: 8,
      padding: 24,
      boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
      border: "1px solid #e2e8f0",
      height: "calc(100vh - 120px)",
      display: "flex",
      flexDirection: "column",
      ...style,
    }}
  >
    {children}
  </div>
);

export const LogInteractionChat = () => {
  const dispatch = useDispatch();
  const { loading = false, chatToolResult = null, error = null } = useSelector(
    (state) => state?.interaction || {}
  );

  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, chatToolResult]);

  useEffect(() => {
    if (chatToolResult?.tool_result) {
      const tool = chatToolResult.tool_result;
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          content: `Interaction logged successfully!\n\nHCP: ${tool.hcp_name || "N/A"}\nSpecialty: ${tool.specialty || "N/A"}\nProducts: ${tool.products_discussed || "N/A"}\nSentiment: ${tool.sentiment || "N/A"}\n\nSummary: ${tool.summary || "No summary available"}`,
        },
      ]);
    }
  }, [chatToolResult]);

  useEffect(() => {
    if (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          content: `Error: ${error}`,
        },
      ]);
    }
  }, [error]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || loading) return;

    // Add user message
    const userMessage = {
      type: "user",
      content: inputText,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");

    // Dispatch chat interaction
    dispatch(
      createChatInteraction({
        free_text: inputText,
        channel: "Meeting", // Default, can be enhanced
      })
    );
  };

  return (
    <Card>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <h2
          style={{
            fontSize: 18,
            fontWeight: 600,
            color: "#1e293b",
            marginBottom: 4,
            marginTop: 0,
          }}
        >
          AI Assistant
        </h2>
        <p
          style={{
            fontSize: 13,
            color: "#64748b",
            margin: 0,
          }}
        >
          Log interaction via chat
        </p>
      </div>

      {/* Messages Area */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          marginBottom: 16,
          padding: "16px 0",
          borderTop: "1px solid #e2e8f0",
          borderBottom: "1px solid #e2e8f0",
        }}
      >
        {messages.length === 0 ? (
          <div
            style={{
              padding: "40px 20px",
              textAlign: "center",
              color: "#94a3b8",
              fontSize: 14,
              fontStyle: "italic",
            }}
          >
            Log interaction details here (e.g. 'Met Dr. Smith, discussed Product X...')
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  alignSelf: msg.type === "user" ? "flex-end" : "flex-start",
                  maxWidth: "85%",
                }}
              >
                <div
                  style={{
                    padding: "12px 16px",
                    borderRadius: 8,
                    backgroundColor:
                      msg.type === "user" ? "#2563eb" : "#f1f5f9",
                    color: msg.type === "user" ? "#ffffff" : "#1e293b",
                    fontSize: 14,
                    lineHeight: 1.5,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div
                style={{
                  alignSelf: "flex-start",
                  padding: "12px 16px",
                  borderRadius: 8,
                  backgroundColor: "#f1f5f9",
                  fontSize: 14,
                  color: "#64748b",
                }}
              >
                Processing...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit}>
        <div style={{ display: "flex", gap: 8 }}>
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your interaction details here..."
            rows={3}
            style={{
              flex: 1,
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
              resize: "none",
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            style={{
              padding: "12px 24px",
              borderRadius: 6,
              border: "none",
              background:
                loading || !inputText.trim() ? "#cbd5e1" : "#2563eb",
              color: "#ffffff",
              fontSize: 14,
              fontWeight: 600,
              cursor:
                loading || !inputText.trim() ? "not-allowed" : "pointer",
              fontFamily: "Inter, sans-serif",
              alignSelf: "flex-end",
              whiteSpace: "nowrap",
            }}
          >
            Log
          </button>
        </div>
      </form>
    </Card>
  );
};

export default LogInteractionChat;
