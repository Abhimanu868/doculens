"use client";

import { useEffect, useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import StatsBar from "../components/StatsBar";
import DocumentUpload from "../components/DocumentUpload";
import DocumentList from "../components/DocumentList";
import SemanticSearch from "../components/SemanticSearch";
import NLIStudio from "../components/NLIStudio";
import DocumentModal from "../components/DocumentModal";

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

export default function Home() {
  const [activeTab, setActiveTab] = useState("documents"); // "documents" | "search" | "nli"
  const [backendStatus, setBackendStatus] = useState({ online: false, checking: true });
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [selectedDocForModal, setSelectedDocForModal] = useState(null);
  const [searchDocFilter, setSearchDocFilter] = useState(null);
  const [nliInitialPremise, setNliInitialPremise] = useState("");

  // Health check
  const checkHealth = useCallback(() => {
    fetch(`${API_URL}/health`)
      .then((res) => {
        if (!res.ok) throw new Error("Offline");
        return res.json();
      })
      .then(() => {
        setBackendStatus({ online: true, checking: false });
      })
      .catch(() => {
        setBackendStatus({ online: false, checking: false });
      });
  }, []);

  // Fetch documents
  const fetchDocuments = useCallback(() => {
    setLoadingDocs(true);
    fetch(`${API_URL}/api/documents`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch documents");
        return res.json();
      })
      .then((data) => {
        setDocuments(data.documents || []);
        setLoadingDocs(false);
      })
      .catch((err) => {
        console.error("Error fetching documents:", err);
        setDocuments([]);
        setLoadingDocs(false);
      });
  }, []);

  useEffect(() => {
    checkHealth();
    fetchDocuments();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, [checkHealth, fetchDocuments]);

  // Document upload callback
  const handleUploadSuccess = () => {
    fetchDocuments();
  };

  // Delete document callback
  const handleDeleteDocument = async (docId) => {
    if (!confirm("Are you sure you want to delete this document and remove its vectors from the FAISS index?")) {
      return;
    }
    try {
      const res = await fetch(`${API_URL}/api/documents/${docId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete document");
      fetchDocuments();
    } catch (err) {
      alert(err.message || "Delete failed");
    }
  };

  // Switch to search with document filter
  const handleSearchInDoc = (docId) => {
    setSearchDocFilter(docId);
    setActiveTab("search");
  };

  // Switch from Search result to NLI Studio with premise
  const handleSendToNLI = (text) => {
    setNliInitialPremise(text);
    setActiveTab("nli");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
        documentCount={documents.length}
      />

      {/* Main Container */}
      <main style={{ flex: 1, maxWidth: "1280px", width: "100%", margin: "0 auto", padding: "32px 24px" }}>
        {/* Metric / Stats Overview */}
        <StatsBar documents={documents} />

        {/* Tab 1: Documents & Ingestion */}
        {activeTab === "documents" && (
          <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column" }}>
            <DocumentUpload onUploadSuccess={handleUploadSuccess} apiUrl={API_URL} />
            <DocumentList
              documents={documents}
              loading={loadingDocs}
              onSelectDocument={(doc) => setSelectedDocForModal(doc)}
              onSearchInDocument={handleSearchInDoc}
              onDeleteDocument={handleDeleteDocument}
            />
          </div>
        )}

        {/* Tab 2: Semantic Similarity Search */}
        {activeTab === "search" && (
          <div className="animate-fade-in">
            <SemanticSearch
              apiUrl={API_URL}
              documents={documents}
              selectedDocId={searchDocFilter}
              onSendToNLI={handleSendToNLI}
            />
          </div>
        )}

        {/* Tab 3: Natural Language Inference Studio */}
        {activeTab === "nli" && (
          <div className="animate-fade-in">
            <NLIStudio apiUrl={API_URL} initialPremise={nliInitialPremise} />
          </div>
        )}
      </main>

      {/* Detail / Text Inspector Modal */}
      {selectedDocForModal && (
        <DocumentModal
          doc={selectedDocForModal}
          apiUrl={API_URL}
          onClose={() => setSelectedDocForModal(null)}
        />
      )}

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border)",
        padding: "24px 32px",
        textAlign: "center",
        color: "var(--fg-muted)",
        fontSize: "0.82rem",
        background: "rgba(10, 12, 18, 0.8)",
        marginTop: "auto"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", maxWidth: "1280px", margin: "0 auto" }}>
          <div>
            <strong>DocuLens</strong> — Intelligent Document Analysis &amp; NLI Verification Platform
          </div>
          <div style={{ display: "flex", gap: "16px" }}>
            <span>FastAPI Backend ({new URL(API_URL).host})</span>
            <span>•</span>
            <span>Next.js Frontend</span>
            <span>•</span>
            <span>FAISS + spaCy + PyTorch</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
