"use client";

import React, { useState, useRef } from "react";

export default function DocumentUpload({ onUploadSuccess, apiUrl }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState("");
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file) => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are currently supported for extraction and indexing.");
      return;
    }
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000);

    setUploading(true);
    setError(null);
    setSuccessMsg(null);
    setUploadProgress("Uploading and processing; this may take a minute…");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setUploadProgress("Extracting text via PyMuPDF and segmenting sentences…");
      const res = await fetch(`${apiUrl}/api/upload`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      let data = null;
      try {
        data = await res.json();
      } catch {
        data = null;
      }

      if (!res.ok) {
        throw new Error(data?.detail || `Upload failed with status ${res.status}`);
      }

      setSuccessMsg(`Successfully processed "${file.name}" — ${data.num_chunks} text chunks embedded and indexed!`);
      if (fileInputRef.current) fileInputRef.current.value = "";
      if (onUploadSuccess) onUploadSuccess(data);
    } catch (err) {
      const message = err?.name === "AbortError"
        ? "Upload timed out after 3 minutes. Try a smaller PDF or retry when the service is ready."
        : (err?.message || "Failed to upload document");
      setError(message);
    } finally {
      clearTimeout(timeoutId);
      setUploading(false);
      setUploadProgress("");
    }
  };

  return (
    <div className="glass-panel" style={{ padding: "28px", marginBottom: "28px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
        <div>
          <h2 style={{ fontSize: "1.15rem", fontWeight: "700" }}>Upload &amp; Index Document</h2>
          <p style={{ fontSize: "0.86rem", color: "var(--fg-muted)", marginTop: "4px" }}>
            PDF documents are automatically parsed, split into clean sentences with spaCy, converted to 384-d vector embeddings, and stored in FAISS.
          </p>
        </div>
      </div>

      {/* Drag & Drop Box */}
      <div
        id="upload-dropzone"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${isDragging ? "var(--accent)" : "rgba(255, 255, 255, 0.15)"}`,
          background: isDragging ? "rgba(94, 129, 244, 0.08)" : "rgba(0, 0, 0, 0.2)",
          borderRadius: "var(--radius-md)",
          padding: "36px 20px",
          textAlign: "center",
          cursor: uploading ? "wait" : "pointer",
          transition: "all 0.2s ease"
        }}
      >
        <input
          id="file-upload-input"
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={handleFileChange}
          disabled={uploading}
        />

        <div style={{ fontSize: "2.4rem", marginBottom: "12px" }}>
          {uploading ? "⏳" : isDragging ? "📥" : "📄"}
        </div>

        {uploading ? (
          <div>
            <div style={{ fontWeight: "600", color: "var(--accent-light)", fontSize: "0.95rem" }}>
              Processing Pipeline Active
            </div>
            <div style={{ fontSize: "0.84rem", color: "var(--fg-muted)", marginTop: "6px" }}>
              {uploadProgress}
            </div>
          </div>
        ) : (
          <div>
            <div style={{ fontWeight: "600", fontSize: "0.95rem" }}>
              Drop your PDF here, or <span style={{ color: "var(--accent-light)", textDecoration: "underline" }}>browse file</span>
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--fg-muted)", marginTop: "6px" }}>
              Supports PDF documents; the server enforces the configured upload size limit.
            </div>
          </div>
        )}
      </div>

      {/* Status Messages */}
      {error && (
        <div style={{
          marginTop: "16px",
          padding: "12px 16px",
          borderRadius: "var(--radius-sm)",
          background: "rgba(239, 68, 68, 0.1)",
          border: "1px solid rgba(239, 68, 68, 0.3)",
          color: "#fca5a5",
          fontSize: "0.88rem",
          display: "flex",
          alignItems: "center",
          gap: "10px"
        }}>
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div style={{
          marginTop: "16px",
          padding: "12px 16px",
          borderRadius: "var(--radius-sm)",
          background: "rgba(16, 185, 129, 0.1)",
          border: "1px solid rgba(16, 185, 129, 0.3)",
          color: "#6ee7b7",
          fontSize: "0.88rem",
          display: "flex",
          alignItems: "center",
          gap: "10px"
        }}>
          <span>✅</span>
          <span>{successMsg}</span>
        </div>
      )}
    </div>
  );
}
