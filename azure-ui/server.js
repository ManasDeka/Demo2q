const express = require("express");

const app = express();
const PORT = 3000;

// Serve the static UI files (index.html, etc.)
app.use(express.static("public"));

// Parse JSON bodies from fetch()
app.use(express.json());

// This endpoint will receive the user question and forward it to FastAPI
app.post("/ask", async (req, res) => {
try {
const { question } = req.body;

if (!question) {
return res.status(400).json({ error: "Missing 'question' in request body" });
}

// IMPORTANT: FastAPI must be running on port 8000
const fastapiUrl = "http://127.0.0.1:8000/ask";

const response = await fetch(fastapiUrl, {
method: "POST",
headers: { "Content-Type": "application/json" },
body: JSON.stringify({ question }),
});

const data = await response.json();
return res.status(response.status).json(data);
} catch (err) {
return res.status(500).json({ error: "Node server error", details: String(err) });
}
});

app.listen(PORT, () => {
console.log(`UI running at: http://127.0.0.1:${PORT}`);
});