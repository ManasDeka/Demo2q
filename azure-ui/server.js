const express = require("express");

const app = express();

// Render injects the port in process.env.PORT. DO NOT hardcode 3000.
const PORT = process.env.PORT || 3000;

// Base URL of your FastAPI backend on Render (e.g., https://your-backend.onrender.com).
// We'll read it from env so we can configure it in the Render dashboard.
const API_BASE = process.env.API_BASE; // REQUIRED

// Serve static UI files (public/index.html, etc.)
app.use(express.static("public"));

// Parse JSON bodies from fetch()
app.use(express.json());

// Simple health for debugging
app.get("/healthz", (_req, res) => res.json({ ok: true, apiBase: API_BASE || null }));

// Proxy endpoint: UI → (this server) → FastAPI
app.post("/ask", async (req, res) => {
  try {
    const { question } = req.body;
    if (!question) {
      return res.status(400).json({ error: "Missing 'question' in request body" });
    }

    if (!API_BASE) {
      return res.status(500).json({
        error: "Server not configured",
        details: "Missing API_BASE env var (backend base URL).",
      });
    }

    const fastapiUrl = `${API_BASE.replace(/\/+$/, "")}/ask`; // ensure single slash

    const response = await fetch(fastapiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    // Forward backend response (status + JSON) to the browser
    const data = await response.json().catch(() => ({}));
    return res.status(response.status).json(data);
  } catch (err) {
    return res.status(500).json({ error: "Node server error", details: String(err) });
  }
});

app.listen(PORT, () => {
  console.log(`UI running on port ${PORT}, using API_BASE=${API_BASE || "(not set)"}`);
});