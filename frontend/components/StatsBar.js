"use client";

import React from "react";

export default function StatsBar({ documents = [] }) {
  const totalDocs = documents.length;
  const totalChunks = documents.reduce((acc, d) => acc + (d.num_chunks || 0), 0);
  const totalSizeKB = Math.round(
    documents.reduce((acc, d) => acc + (d.file_size_bytes || 0), 0) / 1024
  );

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
      gap: "16px",
      marginBottom: "28px"
    }}>
      {/* Total Docs */}
      <div className="glass-panel" style={{ padding: "18px 22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--fg-muted)", fontWeight: "500" }}>DOCUMENTS INDEXED</span>
          <span style={{ fontSize: "1.2rem" }}>📁</span>
        </div>
        <div style={{ fontSize: "1.8rem", fontWeight: "700", marginTop: "8px", color: "var(--fg)" }}>
          {totalDocs}
        </div>
        <div style={{ fontSize: "0.78rem", color: "var(--fg-muted)", marginTop: "4px" }}>
          {totalSizeKB > 0 ? `${totalSizeKB} KB processed` : "No files uploaded"}
        </div>
      </div>

      {/* Total Chunks */}
      <div className="glass-panel" style={{ padding: "18px 22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--fg-muted)", fontWeight: "500" }}>EMBEDDED CHUNKS</span>
          <span style={{ fontSize: "1.2rem" }}>🧩</span>
        </div>
        <div style={{ fontSize: "1.8rem", fontWeight: "700", marginTop: "8px", color: "var(--accent-light)" }}>
          {totalChunks.toLocaleString()}
        </div>
        <div style={{ fontSize: "0.78rem", color: "var(--fg-muted)", marginTop: "4px" }}>
          Segmented via spaCy en_core_web_sm
        </div>
      </div>

      {/* Vector Store */}
      <div className="glass-panel" style={{ padding: "18px 22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--fg-muted)", fontWeight: "500" }}>FAISS VECTOR INDEX</span>
          <span style={{ fontSize: "1.2rem" }}>⚡</span>
        </div>
        <div style={{ fontSize: "1.8rem", fontWeight: "700", marginTop: "8px", color: "#34d399" }}>
          {totalChunks} <span style={{ fontSize: "0.9rem", fontWeight: "500", color: "var(--fg-muted)" }}>vectors (384-d)</span>
        </div>
        <div style={{ fontSize: "0.78rem", color: "var(--fg-muted)", marginTop: "4px" }}>
          Cosine Similarity IndexFlatIP
        </div>
      </div>

      {/* NLI Classifier Model */}
      <div className="glass-panel" style={{ padding: "18px 22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: "0.82rem", color: "var(--fg-muted)", fontWeight: "500" }}>NLI CLASSIFIER</span>
          <span style={{ fontSize: "1.2rem" }}>🤖</span>
        </div>
        <div style={{ fontSize: "1rem", fontWeight: "700", marginTop: "8px", color: "#c084fc", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          doculens-nli
        </div>
        <div style={{ fontSize: "0.78rem", color: "var(--fg-muted)", marginTop: "4px" }}>
          HuggingFace: Abhimanyu125047
        </div>
      </div>
    </div>
  );
}
