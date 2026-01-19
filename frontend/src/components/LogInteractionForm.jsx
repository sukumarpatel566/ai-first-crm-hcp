import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createStructuredInteraction } from "../redux/interactionSlice";

// Card container component
const Card = ({ children, style = {} }) => (
  <div
    style={{
      backgroundColor: "#ffffff",
      borderRadius: 8,
      padding: 24,
      boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
      border: "1px solid #e2e8f0",
      ...style,
    }}
  >
    {children}
  </div>
);

// Section header component
const SectionHeader = ({ title }) => (
  <h3
    style={{
      fontSize: 16,
      fontWeight: 600,
      color: "#1e293b",
      marginBottom: 16,
      marginTop: 0,
    }}
  >
    {title}
  </h3>
);

// Form field component
const FormField = ({ label, children, required = false }) => (
  <div style={{ marginBottom: 16 }}>
    <label
      style={{
        display: "block",
        fontSize: 14,
        fontWeight: 500,
        color: "#475569",
        marginBottom: 6,
      }}
    >
      {label}
      {required && <span style={{ color: "#ef4444", marginLeft: 4 }}>*</span>}
    </label>
    {children}
  </div>
);

export const LogInteractionForm = () => {
  const dispatch = useDispatch();
  const { loading = false, lastInteraction = null } = useSelector(
    (state) => state?.interaction || {}
  );

  const [form, setForm] = useState({
    hcp_name: "",
    interaction_type: "Meeting",
    date: new Date().toISOString().split("T")[0],
    time: new Date().toTimeString().slice(0, 5),
    attendees: "",
    topics_discussed: "",
    materials_shared: [],
    samples_distributed: [],
    sentiment: "Neutral",
    outcomes: "",
    follow_up_actions: "",
  });

  const [newMaterial, setNewMaterial] = useState("");
  const [newSample, setNewSample] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddMaterial = () => {
    if (newMaterial.trim()) {
      setForm((prev) => ({
        ...prev,
        materials_shared: [...prev.materials_shared, newMaterial.trim()],
      }));
      setNewMaterial("");
    }
  };

  const handleRemoveMaterial = (index) => {
    setForm((prev) => ({
      ...prev,
      materials_shared: prev.materials_shared.filter((_, i) => i !== index),
    }));
  };

  const handleAddSample = () => {
    if (newSample.trim()) {
      setForm((prev) => ({
        ...prev,
        samples_distributed: [...prev.samples_distributed, newSample.trim()],
      }));
      setNewSample("");
    }
  };

  const handleRemoveSample = (index) => {
    setForm((prev) => ({
      ...prev,
      samples_distributed: prev.samples_distributed.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const interactionDate = new Date(
      `${form.date}T${form.time}`
    ).toISOString();
    
    const payload = {
      hcp_name: form.hcp_name,
      channel: form.interaction_type,
      interaction_date: interactionDate,
      products_discussed: form.topics_discussed || null,
      notes: [
        form.attendees && `Attendees: ${form.attendees}`,
        form.materials_shared.length > 0 &&
          `Materials Shared: ${form.materials_shared.join(", ")}`,
        form.samples_distributed.length > 0 &&
          `Samples Distributed: ${form.samples_distributed.join(", ")}`,
        form.outcomes && `Outcomes: ${form.outcomes}`,
        form.follow_up_actions && `Follow-up Actions: ${form.follow_up_actions}`,
      ]
        .filter(Boolean)
        .join("\n"),
      sentiment: form.sentiment,
    };
    
    dispatch(createStructuredInteraction(payload));
  };

  return (
    <Card>
      <form onSubmit={handleSubmit}>
        {/* A. Interaction Details */}
        <SectionHeader title="Interaction Details" />
        
        <FormField label="HCP Name" required>
          <input
            type="text"
            name="hcp_name"
            value={form.hcp_name}
            onChange={handleChange}
            required
            placeholder="Search or select HCP"
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
            }}
          />
        </FormField>

        <FormField label="Interaction Type" required>
          <select
            name="interaction_type"
            value={form.interaction_type}
            onChange={handleChange}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
              backgroundColor: "#ffffff",
            }}
          >
            <option value="Meeting">Meeting</option>
            <option value="Call">Call</option>
            <option value="Virtual">Virtual</option>
          </select>
        </FormField>

        <div style={{ display: "flex", gap: 16 }}>
          <div style={{ flex: 1 }}>
            <FormField label="Date" required>
              <input
                type="date"
                name="date"
                value={form.date}
                onChange={handleChange}
                required
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: 6,
                  border: "1px solid #cbd5e1",
                  fontSize: 14,
                  fontFamily: "Inter, sans-serif",
                }}
              />
            </FormField>
          </div>
          <div style={{ flex: 1 }}>
            <FormField label="Time" required>
              <input
                type="time"
                name="time"
                value={form.time}
                onChange={handleChange}
                required
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: 6,
                  border: "1px solid #cbd5e1",
                  fontSize: 14,
                  fontFamily: "Inter, sans-serif",
                }}
              />
            </FormField>
          </div>
        </div>

        <FormField label="Attendees">
          <input
            type="text"
            name="attendees"
            value={form.attendees}
            onChange={handleChange}
            placeholder="Enter attendee names"
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
            }}
          />
        </FormField>

        <FormField label="Topics Discussed">
          <textarea
            name="topics_discussed"
            value={form.topics_discussed}
            onChange={handleChange}
            rows={4}
            placeholder="Enter topics discussed during the interaction"
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
              resize: "vertical",
            }}
          />
        </FormField>

        <div style={{ marginBottom: 16 }}>
          <button
            type="button"
            style={{
              padding: "8px 16px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              backgroundColor: "#f8fafc",
              fontSize: 14,
              fontWeight: 500,
              color: "#475569",
              cursor: "pointer",
            }}
          >
            Summarize from Voice Note
          </button>
        </div>

        {/* B. Materials Shared / Samples Distributed */}
        <SectionHeader title="Materials Shared / Samples Distributed" />

        <FormField label="Materials Shared">
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <input
              type="text"
              value={newMaterial}
              onChange={(e) => setNewMaterial(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddMaterial())}
              placeholder="Search or add material"
              style={{
                flex: 1,
                padding: "10px 12px",
                borderRadius: 6,
                border: "1px solid #cbd5e1",
                fontSize: 14,
                fontFamily: "Inter, sans-serif",
              }}
            />
            <button
              type="button"
              onClick={handleAddMaterial}
              style={{
                padding: "10px 16px",
                borderRadius: 6,
                border: "1px solid #cbd5e1",
                backgroundColor: "#f1f5f9",
                fontSize: 14,
                fontWeight: 500,
                color: "#475569",
                cursor: "pointer",
              }}
            >
              Add
            </button>
          </div>
          {form.materials_shared.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {form.materials_shared.map((material, index) => (
                <span
                  key={index}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "6px 12px",
                    borderRadius: 6,
                    backgroundColor: "#f1f5f9",
                    fontSize: 13,
                    color: "#475569",
                  }}
                >
                  {material}
                  <button
                    type="button"
                    onClick={() => handleRemoveMaterial(index)}
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#64748b",
                      cursor: "pointer",
                      fontSize: 16,
                      lineHeight: 1,
                      padding: 0,
                      marginLeft: 4,
                    }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </FormField>

        <FormField label="Samples Distributed">
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <input
              type="text"
              value={newSample}
              onChange={(e) => setNewSample(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddSample())}
              placeholder="Add sample"
              style={{
                flex: 1,
                padding: "10px 12px",
                borderRadius: 6,
                border: "1px solid #cbd5e1",
                fontSize: 14,
                fontFamily: "Inter, sans-serif",
              }}
            />
            <button
              type="button"
              onClick={handleAddSample}
              style={{
                padding: "10px 16px",
                borderRadius: 6,
                border: "1px solid #cbd5e1",
                backgroundColor: "#f1f5f9",
                fontSize: 14,
                fontWeight: 500,
                color: "#475569",
                cursor: "pointer",
              }}
            >
              Add Sample
            </button>
          </div>
          {form.samples_distributed.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {form.samples_distributed.map((sample, index) => (
                <span
                  key={index}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                    padding: "6px 12px",
                    borderRadius: 6,
                    backgroundColor: "#f1f5f9",
                    fontSize: 13,
                    color: "#475569",
                  }}
                >
                  {sample}
                  <button
                    type="button"
                    onClick={() => handleRemoveSample(index)}
                    style={{
                      border: "none",
                      background: "transparent",
                      color: "#64748b",
                      cursor: "pointer",
                      fontSize: 16,
                      lineHeight: 1,
                      padding: 0,
                      marginLeft: 4,
                    }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          )}
        </FormField>

        {/* C. Observed / Inferred HCP Sentiment */}
        <SectionHeader title="Observed / Inferred HCP Sentiment" />

        <FormField label="Sentiment">
          <div style={{ display: "flex", gap: 16 }}>
            {["Positive", "Neutral", "Negative"].map((sentiment) => (
              <label
                key={sentiment}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  cursor: "pointer",
                  fontSize: 14,
                  color: "#475569",
                }}
              >
                <input
                  type="radio"
                  name="sentiment"
                  value={sentiment}
                  checked={form.sentiment === sentiment}
                  onChange={handleChange}
                  style={{ cursor: "pointer" }}
                />
                {sentiment}
              </label>
            ))}
          </div>
        </FormField>

        {/* D. Outcomes */}
        <SectionHeader title="Outcomes" />

        <FormField label="Outcomes or Agreements">
          <textarea
            name="outcomes"
            value={form.outcomes}
            onChange={handleChange}
            rows={4}
            placeholder="Enter outcomes or agreements from the interaction"
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
              resize: "vertical",
            }}
          />
        </FormField>

        {/* E. Follow-up Actions */}
        <SectionHeader title="Follow-up Actions" />

        <FormField label="Follow-up Actions">
          <textarea
            name="follow_up_actions"
            value={form.follow_up_actions}
            onChange={handleChange}
            rows={4}
            placeholder="Enter next steps or follow-up actions"
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: 6,
              border: "1px solid #cbd5e1",
              fontSize: 14,
              fontFamily: "Inter, sans-serif",
              resize: "vertical",
            }}
          />
        </FormField>

        {/* AI Suggested Follow-ups */}
        {lastInteraction?.follow_up_action && (
          <div style={{ marginTop: 12, marginBottom: 16 }}>
            <div
              style={{
                fontSize: 13,
                fontWeight: 500,
                color: "#64748b",
                marginBottom: 8,
              }}
            >
              AI Suggested Follow-ups:
            </div>
            <ul
              style={{
                margin: 0,
                paddingLeft: 20,
                fontSize: 14,
                color: "#475569",
              }}
            >
              <li>{lastInteraction.follow_up_action}</li>
            </ul>
          </div>
        )}

        {/* Submit Button */}
        <div style={{ marginTop: 24, display: "flex", justifyContent: "flex-end" }}>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "12px 24px",
              borderRadius: 6,
              border: "none",
              background: loading ? "#cbd5e1" : "#2563eb",
              color: "#ffffff",
              fontSize: 14,
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
              fontFamily: "Inter, sans-serif",
            }}
          >
            {loading ? "Saving..." : "Save Interaction"}
          </button>
        </div>
      </form>
    </Card>
  );
};

export default LogInteractionForm;
