"use client";

import React from "react";

export default function Navbar({ activeTab, setActiveTab, backendStatus, documentCount }) {
  return (
    <header style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "16px 32px",
      borderBottom: "1px solid var(--border)",
      background: "rgba(12, 15, 24, 0.8)",
      backdropFilter: "blur(12px)",
      position: "sticky",
      top: 0,
      zIndex: 100
    }}>
      {/* Brand */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        <div style={{
          width: "42px",
          height: "42px",
          borderRadius: "12px",
          background: "linear-gradient(135deg, #5e81f4 0%, #8c52ff 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 20px rgba(94, 129, 244, 0.4)",
          fontSize: "20px"
        }}>
          🔍
        </div>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <h1 style={{ fontSize: "1.25rem", fontWeight: "700", letterSpacing: "-0.02em" }}>DocuLens</h1>
            <span style={{
              fontSize: "0.7rem",
              padding: "2px 8px",
              borderRadius: "6px",
              background: "rgba(94, 129, 244, 0.15)",
              color: "var(--accent-light)",
              border: "1px solid rgba(94, 129, 244, 0.3)",
              fontWeight: "600"
            }}>v0.2.0</span>
          </div>
          <p style={{ fontSize: "0.8rem", color: "var(--fg-muted)", marginTop: "1px" }}>
            Neural Document Intelligence &amp; NLI Verification
          </p>
        </div>
      </div>

      {/* Tabs */}
      <nav style={{
        display: "flex",
        background: "rgba(255, 255, 255, 0.04)",
        padding: "4px",
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--border)"
      }}>
        <button
          id="nav-tab-documents"
          onClick={() => setActiveTab("documents")}
          style={{
            padding: "8px 18px",
            borderRadius: "var(--radius-sm)",
            border: "none",
            background: activeTab === "documents" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "documents" ? "#ffffff" : "var(--fg-secondary)",
            fontWeight: "600",
            fontSize: "0.88rem",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "all 0.2s ease"
          }}
        >
          <span>📄 Documents</span>
          {documentCount > 0 && (
            <span style={{
              background: activeTab === "documents" ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.08)",
              padding: "1px 6px",
              borderRadius: "10px",
              fontSize: "0.75rem"
            }}>{documentCount}</span>
          )}
        </button>

        <button
          id="nav-tab-search"
          onClick={() => setActiveTab("search")}
          style={{
            padding: "8px 18px",
            borderRadius: "var(--radius-sm)",
            border: "none",
            background: activeTab === "search" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "search" ? "#ffffff" : "var(--fg-secondary)",
            fontWeight: "600",
            fontSize: "0.88rem",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "all 0.2s ease"
          }}
        >
          <span>⚡ Semantic Search</span>
        </button>

        <button
          id="nav-tab-nli"
          onClick={() => setActiveTab("nli")}
          style={{
            padding: "8px 18px",
            borderRadius: "var(--radius-sm)",
            border: "none",
            background: activeTab === "nli" ? "var(--accent-gradient)" : "transparent",
            color: activeTab === "nli" ? "#ffffff" : "var(--fg-secondary)",
            fontWeight: "600",
            fontSize: "0.88rem",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "all 0.2s ease"
          }}
        >
          <span>🧠 NLI Inference Studio</span>
        </button>
      </nav>

      {/* Live Status indicator */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "6px 14px",
          borderRadius: "var(--radius-full)",
          background: backendStatus.online ? "rgba(16, 185, 129, 0.08)" : "rgba(239, 68, 68, 0.08)",
          border: `1px solid ${backendStatus.online ? "rgba(16, 185, 129, 0.25)" : "rgba(239, 68, 68, 0.25)"}`
        }}>
          <span style={{
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            background: backendStatus.online ? "#10b981" : "#ef4444",
            boxShadow: backendStatus.online ? "0 0 10px #10b981" : "none"
          }} />
          <span style={{
            fontSize: "0.82rem",
            fontWeight: "500",
            color: backendStatus.online ? "#34d399" : "#f87171"
          }}>
            {backendStatus.online ? "Backend Online" : "Backend Offline"}
          </span>
        </div>
      </div>
    </header>
  );
}
