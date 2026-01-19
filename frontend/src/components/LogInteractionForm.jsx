import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createStructuredInteraction } from "../redux/interactionSlice";

// Simple styled card container using Inter font from global CSS.
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

export const LogInteractionForm = () => {
  const dispatch = useDispatch();
  const { loading = false, lastInteraction = null } = useSelector((state) => state?.interaction || {});

  const [form, setForm] = useState({
    hcp_name: "",
    specialty: "",
    interaction_date: new Date().toISOString().slice(0, 16),
    channel: "In-Person",
    products_discussed: "",
    notes: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      interaction_date: new Date(form.interaction_date).toISOString(),
      specialty: form.specialty || null,
      products_discussed: form.products_discussed || null,
      notes: form.notes || null,
    };
    dispatch(createStructuredInteraction(payload));
  };

  return (
    <Card>
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>
        Structured Interaction Log
      </h2>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
        <div style={{ display: "grid", gap: 8 }}>
          <label style={{ fontWeight: 500 }}>HCP Name</label>
          <input
            name="hcp_name"
            value={form.hcp_name}
            onChange={handleChange}
            required
            style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1" }}
            placeholder="Dr. Jane Doe"
          />
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label style={{ fontWeight: 500 }}>Specialty</label>
          <input
            name="specialty"
            value={form.specialty}
            onChange={handleChange}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1" }}
            placeholder="Cardiology"
          />
        </div>

        <div style={{ display: "flex", gap: 16 }}>
          <div style={{ flex: 1, display: "grid", gap: 8 }}>
            <label style={{ fontWeight: 500 }}>Interaction Date</label>
            <input
              type="datetime-local"
              name="interaction_date"
              value={form.interaction_date}
              onChange={handleChange}
              required
              style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1" }}
            />
          </div>
          <div style={{ flex: 1, display: "grid", gap: 8 }}>
            <label style={{ fontWeight: 500 }}>Channel</label>
            <select
              name="channel"
              value={form.channel}
              onChange={handleChange}
              style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1" }}
            >
              <option>In-Person</option>
              <option>Call</option>
              <option>Virtual</option>
            </select>
          </div>
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label style={{ fontWeight: 500 }}>Products Discussed</label>
          <input
            name="products_discussed"
            value={form.products_discussed}
            onChange={handleChange}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1" }}
            placeholder="Product A, Product B"
          />
        </div>

        <div style={{ display: "grid", gap: 8 }}>
          <label style={{ fontWeight: 500 }}>Notes</label>
          <textarea
            name="notes"
            rows={4}
            value={form.notes}
            onChange={handleChange}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #cbd5f1", resize: "vertical" }}
            placeholder="Detail any key discussion points, objections, and follow-ups..."
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            marginTop: 8,
            padding: "10px 16px",
            borderRadius: 999,
            border: "none",
            background: loading ? "#cbd5f1" : "linear-gradient(90deg,#2563eb,#4f46e5)",
            color: "white",
            fontWeight: 600,
            cursor: loading ? "default" : "pointer",
          }}
        >
          {loading ? "Saving..." : "Save Interaction"}
        </button>
      </form>

      {lastInteraction && (
        <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid #e2e8f0" }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Last Saved Interaction</h3>
          <p style={{ fontSize: 14, color: "#4b5563" }}>
            {lastInteraction.summary || "No AI summary available yet."}
          </p>
        </div>
      )}
    </Card>
  );
};

export default LogInteractionForm;

