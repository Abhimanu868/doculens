"use client";

import React, { useEffect, useState } from "react";

export default function DocumentModal({ doc, apiUrl, onClose }) {
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!doc) return;
    setLoading(true);
    fetch(`${apiUrl}/api/documents/${doc.id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load details");
        return res.json();
      })
      .then((data) => {
        setDetails(data);
        setLoading(false);
      })
      .catch(() => {
        setDetails(doc);
        setLoading(false);
      });
  }, [doc, apiUrl]);

  if (!doc) return null;

  const handleCopy = () => {
    if (details?.extracted_text) {
      navigator.clipboard.writeText(details.extracted_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0, 0, 0, 0.75)",
        backdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: "20px"
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="glass-panel animate-fade-in"
        style={{
          width: "100%",
          maxWidth: "800px",
          maxHeight: "85vh",
          display: "flex",
          flexDirection: "column",
          padding: "28px",
          background: "#121624",
          border: "1px solid rgba(255, 255, 255, 0.15)",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.8)"
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span style={{ fontSize: "1.4rem" }}>📄</span>
              <h2 style={{ fontSize: "1.25rem", fontWeight: "700" }}>{doc.filename}</h2>
            </div>
            <p style={{ fontSize: "0.8rem", color: "var(--fg-muted)", fontFamily: "var(--font-mono)", marginTop: "4px" }}>
              Doc ID: {doc.id}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "rgba(255, 255, 255, 0.08)",
              border: "none",
              borderRadius: "50%",
              width: "32px",
              height: "32px",
              color: "var(--fg)",
              fontSize: "1rem",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}
          >
            ✕
          </button>
        </div>

        {/* Metadata Chips */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginBottom: "20px" }}>
          <span className="badge badge-ready">{doc.status || "ready"}</span>
          <span style={{
            fontSize: "0.82rem",
            padding: "4px 10px",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: "var(--radius-sm)",
            color: "var(--fg-secondary)"
          }}>
            <strong>{doc.num_chunks}</strong> text chunks
          </span>
          <span style={{
            fontSize: "0.82rem",
            padding: "4px 10px",
            background: "rgba(255, 255, 255, 0.05)",
            borderRadius: "var(--radius-sm)",
            color: "var(--fg-secondary)"
          }}>
            {(doc.file_size_bytes / 1024).toFixed(1)} KB
          </span>
        </div>

        {/* Extracted Text Content */}
        <div style={{ flex: 1, overflowY: "auto", minHeight: "200px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: "600", color: "var(--fg-muted)" }}>
              EXTRACTED TEXT CONTENT (PyMuPDF)
            </span>
            <button
              onClick={handleCopy}
              className="btn-secondary"
              style={{ padding: "4px 10px", fontSize: "0.78rem" }}
            >
              {copied ? "✓ Copied!" : "📋 Copy Text"}
            </button>
          </div>

          {loading ? (
            <div style={{ padding: "40px", textAlign: "center", color: "var(--fg-muted)" }}>
              Loading extracted text…
            </div>
          ) : details?.extracted_text ? (
            <div style={{
              background: "rgba(0, 0, 0, 0.35)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
              padding: "16px",
              fontSize: "0.9rem",
              lineHeight: "1.7",
              whiteSpace: "pre-wrap",
              color: "var(--fg-secondary)",
              maxHeight: "400px",
              overflowY: "auto"
            }}>
              {details.extracted_text}
            </div>
          ) : (
            <div style={{ padding: "30px", textAlign: "center", color: "var(--fg-muted)" }}>
              No text extracted for this document.
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ marginTop: "20px", display: "flex", justifyContent: "flex-end" }}>
          <button className="btn-secondary" onClick={onClose}>
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
