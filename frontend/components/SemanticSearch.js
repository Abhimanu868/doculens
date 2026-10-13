"use client";

import React, { useState } from "react";

export default function SemanticSearch({
  apiUrl,
  documents = [],
  selectedDocId = null,
  onSendToNLI
}) {
  const [query, setQuery] = useState("");
  const [filterDocId, setFilterDocId] = useState(selectedDocId || "");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setSearching(true);
    setError(null);
    setHasSearched(true);

    try {
      const payload = {
        query: query.trim(),
        top_k: Number(topK),
      };
      if (filterDocId) {
        payload.doc_id = filterDocId;
      }

      const res = await fetch(`${apiUrl}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Search request failed");
      }

      setResults(data.results || []);
    } catch (err) {
      setError(err.message || "Failed to execute semantic search");
    } finally {
      setSearching(false);
    }
  };

  const getDocName = (docId) => {
    const doc = documents.find((d) => d.id === docId);
    return doc ? doc.filename : `Doc ${docId.slice(0, 8)}…`;
  };

  const sampleQueries = [
    "What are the confidentiality and non-disclosure obligations?",
    "What are the requirements for data encryption and security?",
    "How is the termination or cancellation notice handled?",
    "What are the payment terms and invoicing schedule?"
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Search Input Box */}
      <div className="glass-panel" style={{ padding: "28px" }}>
        <h2 style={{ fontSize: "1.2rem", fontWeight: "700" }}>Semantic Similarity Search</h2>
        <p style={{ fontSize: "0.85rem", color: "var(--fg-muted)", marginTop: "4px" }}>
          Embeds your natural language query using SentenceTransformers and queries the FAISS index for high-dimensional cosine similarity matching.
        </p>

        <form onSubmit={handleSearch} style={{ marginTop: "20px", display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <input
              id="search-query-input"
              type="text"
              className="input-field"
              placeholder="e.g. Which clauses govern intellectual property rights and liability limits?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ fontSize: "1rem", padding: "14px 18px" }}
            />
          </div>

          {/* Quick preset queries */}
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "0.78rem", color: "var(--fg-muted)" }}>Suggested queries:</span>
            {sampleQueries.map((sq, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setQuery(sq)}
                style={{
                  background: "rgba(255, 255, 255, 0.04)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--fg-secondary)",
                  fontSize: "0.78rem",
                  padding: "4px 10px",
                  cursor: "pointer",
                  transition: "all 0.15s ease"
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = "var(--accent)")}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
              >
                {sq}
              </button>
            ))}
          </div>

          {/* Controls: Doc Filter & Top-K */}
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "16px",
            alignItems: "center",
            justifyContent: "space-between",
            paddingTop: "8px",
            borderTop: "1px solid rgba(255, 255, 255, 0.05)"
          }}>
            <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
              {/* Document filter dropdown */}
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <label htmlFor="search-filter-doc" style={{ fontSize: "0.82rem", color: "var(--fg-muted)" }}>Scope:</label>
                <select
                  id="search-filter-doc"
                  className="input-field"
                  value={filterDocId}
                  onChange={(e) => setFilterDocId(e.target.value)}
                  style={{ padding: "6px 12px", fontSize: "0.84rem", width: "auto" }}
                >
                  <option value="">All Indexed Documents</option>
                  {documents.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.filename} ({d.num_chunks} chunks)
                    </option>
                  ))}
                </select>
              </div>

              {/* Top-K Selector */}
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <label htmlFor="search-top-k" style={{ fontSize: "0.82rem", color: "var(--fg-muted)" }}>Top Results:</label>
                <select
                  id="search-top-k"
                  className="input-field"
                  value={topK}
                  onChange={(e) => setTopK(e.target.value)}
                  style={{ padding: "6px 12px", fontSize: "0.84rem", width: "auto" }}
                >
                  <option value={3}>Top 3</option>
                  <option value={5}>Top 5</option>
                  <option value={10}>Top 10</option>
                  <option value={20}>Top 20</option>
                </select>
              </div>
            </div>

            <button
              id="search-submit-btn"
              type="submit"
              className="btn-primary"
              disabled={searching || !query.trim()}
              style={{ minWidth: "140px" }}
            >
              {searching ? "Searching FAISS…" : "⚡ Semantic Search"}
            </button>
          </div>
        </form>

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

      {/* Results List */}
      {hasSearched && (
        <div className="glass-panel" style={{ padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <div>
              <h3 style={{ fontSize: "1.1rem", fontWeight: "700" }}>Search Results</h3>
              <p style={{ fontSize: "0.82rem", color: "var(--fg-muted)" }}>
                {results.length} relevant sentence chunks retrieved from FAISS
              </p>
            </div>
          </div>

          {results.length === 0 ? (
            <div style={{ textAlign: "center", padding: "32px", color: "var(--fg-muted)" }}>
              No matching chunks found. Try expanding your search query or uploading more documents.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              {results.map((res, idx) => {
                const scorePercent = Math.max(0, Math.min(100, Math.round(res.score * 100)));
                return (
                  <div
                    key={idx}
                    style={{
                      background: "rgba(255, 255, 255, 0.02)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius-md)",
                      padding: "18px 20px",
                      transition: "all 0.15s ease"
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.borderColor = "rgba(94, 129, 244, 0.4)")}
                    onMouseLeave={(e) => (e.currentTarget.style.borderColor = "var(--border)")}
                  >
                    {/* Header */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <span style={{
                          width: "24px",
                          height: "24px",
                          borderRadius: "50%",
                          background: "rgba(94, 129, 244, 0.15)",
                          color: "var(--accent-light)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: "0.75rem",
                          fontWeight: "700"
                        }}>
                          #{idx + 1}
                        </span>
                        <span style={{ fontSize: "0.85rem", fontWeight: "600", color: "var(--fg-secondary)" }}>
                          {getDocName(res.doc_id)}
                        </span>
                        <span style={{ fontSize: "0.75rem", color: "var(--fg-muted)" }}>
                          (Chunk #{res.chunk_index})
                        </span>
                      </div>

                      {/* Similarity Score */}
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <div style={{
                          width: "80px",
                          height: "6px",
                          background: "rgba(255, 255, 255, 0.1)",
                          borderRadius: "3px",
                          overflow: "hidden"
                        }}>
                          <div style={{
                            width: `${scorePercent}%`,
                            height: "100%",
                            background: scorePercent > 70 ? "#10b981" : scorePercent > 45 ? "#5e81f4" : "#f59e0b",
                            borderRadius: "3px"
                          }} />
                        </div>
                        <span style={{
                          fontSize: "0.82rem",
                          fontFamily: "var(--font-mono)",
                          color: scorePercent > 70 ? "#34d399" : scorePercent > 45 ? "var(--accent-light)" : "#fbbf24",
                          fontWeight: "600"
                        }}>
                          {res.score.toFixed(4)}
                        </span>
                      </div>
                    </div>

                    {/* Matched Text */}
                    <p style={{
                      fontSize: "0.95rem",
                      lineHeight: "1.6",
                      color: "var(--fg)",
                      background: "rgba(0, 0, 0, 0.2)",
                      padding: "12px 14px",
                      borderRadius: "var(--radius-sm)",
                      borderLeft: "3px solid var(--accent)"
                    }}>
                      "{res.text}"
                    </p>

                    {/* Action: Send to NLI */}
                    <div style={{ marginTop: "12px", display: "flex", justifyContent: "flex-end" }}>
                      <button
                        className="btn-secondary"
                        style={{ fontSize: "0.8rem", padding: "6px 12px", gap: "6px" }}
                        onClick={() => onSendToNLI && onSendToNLI(res.text)}
                        title="Send this chunk to NLI Inference Studio as the Premise"
                      >
                        <span>Verify Claim with NLI</span>
                        <span>➜</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
