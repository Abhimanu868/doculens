"use client";

import React from "react";

export default function DocumentList({
  documents = [],
  loading = false,
  onSelectDocument,
  onSearchInDocument,
  onDeleteDocument,
}) {
  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: "32px", textAlign: "center", color: "var(--fg-muted)" }}>
        Loading documents…
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: "40px 24px", textAlign: "center" }}>
        <div style={{ fontSize: "2rem", marginBottom: "8px" }}>📂</div>
        <h3 style={{ fontSize: "1.1rem", fontWeight: "600", color: "var(--fg)" }}>No documents indexed yet</h3>
        <p style={{ fontSize: "0.85rem", color: "var(--fg-muted)", marginTop: "4px" }}>
          Upload a PDF above to extract text, create embeddings, and enable semantic search &amp; NLI.
        </p>
      </div>
    );
  }

  const formatSize = (bytes) => {
    if (!bytes) return "0 B";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return "Just now";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="glass-panel" style={{ padding: "24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <h2 style={{ fontSize: "1.15rem", fontWeight: "700" }}>Indexed Document Repository</h2>
          <p style={{ fontSize: "0.84rem", color: "var(--fg-muted)", marginTop: "2px" }}>
            {documents.length} document{documents.length === 1 ? "" : "s"} stored in SQLite &amp; indexed in FAISS
          </p>
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "0.88rem" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--fg-muted)" }}>
              <th style={{ padding: "12px 16px", fontWeight: "600" }}>DOCUMENT</th>
              <th style={{ padding: "12px 16px", fontWeight: "600" }}>CHUNKS</th>
              <th style={{ padding: "12px 16px", fontWeight: "600" }}>SIZE</th>
              <th style={{ padding: "12px 16px", fontWeight: "600" }}>UPLOADED</th>
              <th style={{ padding: "12px 16px", fontWeight: "600" }}>STATUS</th>
              <th style={{ padding: "12px 16px", fontWeight: "600", textAlign: "right" }}>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr
                key={doc.id}
                style={{
                  borderBottom: "1px solid rgba(255, 255, 255, 0.04)",
                  transition: "background 0.15s ease"
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255, 255, 255, 0.02)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                {/* Filename & ID */}
                <td style={{ padding: "14px 16px" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span style={{ fontSize: "1.2rem" }}>📄</span>
                    <div>
                      <div style={{ fontWeight: "600", color: "var(--fg)" }}>{doc.filename}</div>
                      <div style={{ fontSize: "0.74rem", color: "var(--fg-muted)", fontFamily: "var(--font-mono)" }}>
                        ID: {doc.id.slice(0, 8)}…
                      </div>
                    </div>
                  </div>
                </td>

                {/* Chunks */}
                <td style={{ padding: "14px 16px" }}>
                  <span style={{
                    padding: "3px 8px",
                    borderRadius: "6px",
                    background: "rgba(94, 129, 244, 0.1)",
                    color: "var(--accent-light)",
                    fontWeight: "600",
                    fontSize: "0.82rem"
                  }}>
                    {doc.num_chunks} chunks
                  </span>
                </td>

                {/* Size */}
                <td style={{ padding: "14px 16px", color: "var(--fg-secondary)" }}>
                  {formatSize(doc.file_size_bytes)}
                </td>

                {/* Date */}
                <td style={{ padding: "14px 16px", color: "var(--fg-muted)", fontSize: "0.82rem" }}>
                  {formatDate(doc.upload_time)}
                </td>

                {/* Status */}
                <td style={{ padding: "14px 16px" }}>
                  <span className={`badge badge-${doc.status || "ready"}`}>
                    {doc.status || "ready"}
                  </span>
                </td>

                {/* Actions */}
                <td style={{ padding: "14px 16px", textAlign: "right" }}>
                  <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                    <button
                      className="btn-secondary"
                      style={{ padding: "6px 12px", fontSize: "0.82rem" }}
                      title="Inspect extracted text and metadata"
                      onClick={() => onSelectDocument && onSelectDocument(doc)}
                    >
                      Inspect
                    </button>
                    <button
                      className="btn-secondary"
                      style={{ padding: "6px 12px", fontSize: "0.82rem", color: "var(--accent-light)" }}
                      title="Search inside this document"
                      onClick={() => onSearchInDocument && onSearchInDocument(doc.id)}
                    >
                      Search
                    </button>
                    <button
                      className="btn-danger"
                      style={{ padding: "6px 10px" }}
                      title="Delete document and remove from FAISS"
                      onClick={() => onDeleteDocument && onDeleteDocument(doc.id)}
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
