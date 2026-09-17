"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>
          <span className={styles.logo}>🔍</span> DocuLens
        </h1>
        <p className={styles.subtitle}>
          Intelligent Document Analysis &amp; Semantic Search
        </p>
      </header>

      <main className={styles.main}>
        <section className={styles.card}>
          <h2>Hello DocuLens</h2>
          <p className={styles.description}>
            Your scaffolding is ready. The backend health-check result is shown
            below.
          </p>

          <div className={styles.status}>
            {loading && <span className={styles.loading}>Checking backend…</span>}
            {error && (
              <span className={styles.error}>
                ⚠ Backend unreachable: {error}
              </span>
            )}
            {health && (
              <span className={styles.ok}>
                ✅ Backend status: <code>{JSON.stringify(health)}</code>
              </span>
            )}
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <p>DocuLens v0.1.0 — Phase 1: Scaffolding</p>
      </footer>
    </div>
  );
}
