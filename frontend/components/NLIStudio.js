"use client";

import React, { useState } from "react";

const PRESET_EXAMPLES = [
  {
    category: "Financial / Earnings",
    type: "Contradiction",
    premise: "The company reported a record net profit of $12 million for the third quarter of the fiscal year.",
    hypothesis: "The company suffered massive financial losses in the third quarter."
  },
  {
    category: "Legal / Lease",
    type: "Contradiction",
    premise: "The contract strictly prohibits any subleasing or assignment of the leased premises without prior written consent.",
    hypothesis: "The tenant is completely free to sublease the office space at any time without permission."
  },
  {
    category: "Compliance / Policy",
    type: "Entailment",
    premise: "All employees must complete mandatory cybersecurity training by the end of October.",
    hypothesis: "Cybersecurity training is required for staff members before November."
  },
  {
    category: "Security / Encryption",
    type: "Entailment",
    premise: "The platform encrypts all sensitive customer records using AES-256 both at rest and in transit.",
    hypothesis: "Customer data is encrypted while stored and transmitted."
  },
  {
    category: "Operations / Metrics",
    type: "Neutral",
    premise: "DocuLens successfully processed 5,000 PDF documents during the initial stress testing phase.",
    hypothesis: "The stress test took approximately two hours to finish."
  }
];

export default function NLIStudio({ apiUrl, initialPremise = "" }) {
  const [premise, setPremise] = useState(initialPremise);
  const [hypothesis, setHypothesis] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  // If initialPremise changes from outside (e.g. from Search), update premise
  React.useEffect(() => {
    if (initialPremise) {
      setPremise(initialPremise);
    }
  }, [initialPremise]);

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!premise.trim() || !hypothesis.trim()) return;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000);
    setAnalyzing(true);
    setError(null);

    try {
      const res = await fetch(`${apiUrl}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          premise: premise.trim(),
          hypothesis: hypothesis.trim()
        })
      });

      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error(`The backend returned an unreadable response (HTTP ${res.status}). Please try again.`);
      }
      if (!res.ok) {
        throw new Error(data.detail || `Analysis request failed (HTTP ${res.status}).`);
      }

      setResult(data);
      setHistory((prev) => [
        {
          id: Date.now(),
          premise: data.premise,
          hypothesis: data.hypothesis,
          label: data.label,
          confidence: data.confidence,
          scores: data.scores
        },
        ...prev.slice(0, 7) // keep last 8
      ]);
    } catch (err) {
      setError(err?.name === "AbortError"
        ? "Analysis timed out after 120 seconds. The server may be waking up or busy; please retry."
        : (err?.message === "Failed to fetch"
          ? "Could not reach the backend. It may be waking up; please wait a minute and retry."
          : (err?.message || "Analysis failed. Please try again.")));
    } finally {
      clearTimeout(timeoutId);
      setAnalyzing(false);
    }
  };

  const loadPreset = (preset) => {
    setPremise(preset.premise);
    setHypothesis(preset.hypothesis);
    setResult(null);
    setError(null);
  };

  const getLabelDescription = (label) => {
    switch (label) {
      case "entailment":
        return "The hypothesis is logically guaranteed or confirmed by the premise. The context directly supports this statement.";
      case "contradiction":
        return "The hypothesis directly contradicts or refutes the premise. The claim is mutually incompatible with the context.";
      case "neutral":
        return "The hypothesis might be true or false, but the premise does not provide enough information to confirm or deny it.";
      default:
        return "";
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Studio Card */}
      <div className="glass-panel" style={{ padding: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
          <div>
            <h2 style={{ fontSize: "1.2rem", fontWeight: "700" }}>Natural Language Inference (NLI) Studio</h2>
            <p style={{ fontSize: "0.85rem", color: "var(--fg-muted)", marginTop: "4px" }}>
              Evaluate semantic entailment, factual neutrality, or contradiction between source context and candidate claims using the fine-tuned DocuLens model.
            </p>
          </div>
        </div>

        {/* Quick presets */}
        <div style={{
          background: "rgba(0, 0, 0, 0.2)",
          padding: "14px 18px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border)",
          marginBottom: "20px"
        }}>
          <div style={{ fontSize: "0.8rem", color: "var(--fg-muted)", marginBottom: "8px", fontWeight: "600" }}>
            LOAD BENCHMARK PRESETS:
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {PRESET_EXAMPLES.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadPreset(p)}
                style={{
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  padding: "6px 12px",
                  fontSize: "0.78rem",
                  color: "var(--fg-secondary)",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  transition: "all 0.15s ease"
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
              >
                <span style={{
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: p.type === "Entailment" ? "#10b981" : p.type === "Contradiction" ? "#ef4444" : "#f59e0b"
                }} />
                <span>{p.category} ({p.type})</span>
              </button>
            ))}
          </div>
        </div>

        {/* Inference Form */}
        <form onSubmit={handleAnalyze} style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
          {/* Premise */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <label htmlFor="nli-premise-input" style={{ fontSize: "0.88rem", fontWeight: "600", color: "var(--fg)" }}>
                Premise (Source Context / Document Passage)
              </label>
              <span style={{ fontSize: "0.75rem", color: "var(--fg-muted)" }}>
                {premise.length} characters
              </span>
            </div>
            <textarea
              id="nli-premise-input"
              className="textarea-field"
              placeholder="Enter context sentence or paste from an indexed document chunk…"
              value={premise}
              onChange={(e) => setPremise(e.target.value)}
              rows={3}
            />
          </div>

          {/* Hypothesis */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <label htmlFor="nli-hypothesis-input" style={{ fontSize: "0.88rem", fontWeight: "600", color: "var(--fg)" }}>
                Hypothesis (Claim / Assertion to Test)
              </label>
              <span style={{ fontSize: "0.75rem", color: "var(--fg-muted)" }}>
                {hypothesis.length} characters
              </span>
            </div>
            <input
              id="nli-hypothesis-input"
              type="text"
              className="input-field"
              placeholder="e.g. The company generated positive profit."
              value={hypothesis}
              onChange={(e) => setHypothesis(e.target.value)}
            />
          </div>

          {/* Submit */}
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button
              id="nli-analyze-btn"
              type="submit"
              className="btn-primary"
              disabled={analyzing || !premise.trim() || !hypothesis.trim()}
              style={{ minWidth: "160px" }}
            >
              {analyzing ? "Analyzing, this may take a minute..." : "🧠 Run NLI Inference"}
            </button>
          </div>
        </form>

        {analyzing && (
          <p role="status" style={{ marginTop: "12px", color: "var(--fg-muted)", fontSize: "0.85rem" }}>
            Analyzing, this may take a minute...
          </p>
        )}

        {error && (
          <div style={{
            marginTop: "16px",
            padding: "12px",
            borderRadius: "var(--radius-sm)",
            background: "rgba(239, 68, 68, 0.1)",
            color: "#fca5a5",
            fontSize: "0.85rem"
          }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      {/* Result Display */}
      {result && (
        <div className="glass-panel animate-fade-in" style={{ padding: "28px", border: `1px solid var(--${result.label}-border)` }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <span style={{ fontSize: "0.82rem", color: "var(--fg-muted)", fontWeight: "600", letterSpacing: "0.05em" }}>
              PREDICTION RESULT
            </span>
            <span style={{ fontSize: "0.82rem", color: "var(--fg-muted)" }}>
              Model: <code style={{ color: "var(--accent-light)" }}>doculens-nli</code>
            </span>
          </div>

          {/* Big classification banner */}
          <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: `var(--${result.label}-bg)`,
            border: `1px solid var(--${result.label}-border)`,
            borderRadius: "var(--radius-md)",
            padding: "20px 24px",
            marginBottom: "20px"
          }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <span style={{
                  fontSize: "1.8rem",
                  fontWeight: "800",
                  color: `var(--${result.label})`,
                  textTransform: "uppercase",
                  letterSpacing: "0.04em"
                }}>
                  {result.label}
                </span>
                <span className={`badge badge-${result.label}`}>
                  {(result.confidence * 100).toFixed(1)}% Confidence
                </span>
              </div>
              <p style={{ fontSize: "0.88rem", color: "var(--fg-secondary)", marginTop: "6px", maxWidth: "600px" }}>
                {getLabelDescription(result.label)}
              </p>
            </div>

            <div style={{ fontSize: "2.5rem" }}>
              {result.label === "entailment" ? "✅" : result.label === "contradiction" ? "❌" : "⚖️"}
            </div>
          </div>

          {/* Probability Distribution */}
          <div>
            <div style={{ fontSize: "0.84rem", fontWeight: "600", color: "var(--fg-secondary)", marginBottom: "10px" }}>
              Softmax Probability Distribution
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {[
                { label: "entailment", name: "Entailment", val: result.scores.entailment, color: "#10b981" },
                { label: "neutral", name: "Neutral", val: result.scores.neutral, color: "#f59e0b" },
                { label: "contradiction", name: "Contradiction", val: result.scores.contradiction, color: "#ef4444" }
              ].map((cls) => {
                const pct = (cls.val * 100).toFixed(1);
                return (
                  <div key={cls.label}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", marginBottom: "4px" }}>
                      <span style={{ fontWeight: "600", color: cls.color }}>{cls.name}</span>
                      <span style={{ fontFamily: "var(--font-mono)", color: "var(--fg-muted)" }}>{pct}% ({cls.val.toFixed(4)})</span>
                    </div>
                    <div style={{
                      width: "100%",
                      height: "8px",
                      background: "rgba(255, 255, 255, 0.08)",
                      borderRadius: "4px",
                      overflow: "hidden"
                    }}>
                      <div style={{
                        width: `${pct}%`,
                        height: "100%",
                        background: cls.color,
                        borderRadius: "4px",
                        transition: "width 0.4s cubic-bezier(0.16, 1, 0.3, 1)"
                      }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="glass-panel" style={{ padding: "24px" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: "700", marginBottom: "14px" }}>
            Session Analysis History ({history.length})
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {history.map((item) => (
              <div
                key={item.id}
                style={{
                  background: "rgba(255, 255, 255, 0.02)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  padding: "12px 16px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "16px"
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "0.84rem", color: "var(--fg)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    <strong>Hypothesis:</strong> "{item.hypothesis}"
                  </div>
                  <div style={{ fontSize: "0.78rem", color: "var(--fg-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginTop: "2px" }}>
                    Premise: "{item.premise}"
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span className={`badge badge-${item.label}`}>
                    {item.label}
                  </span>
                  <span style={{ fontSize: "0.78rem", fontFamily: "var(--font-mono)", color: "var(--fg-muted)" }}>
                    {(item.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
