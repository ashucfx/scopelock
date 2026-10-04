# Capability Taxonomy

ScopeLock classifies all detected API calls into **6 capability categories**, each representing a distinct class of system authority.

---

## Categories

### 🌐 NETWORK

Capabilities that establish communication with external systems.

| Action | APIs (JS) | APIs (Python) |
|---|---|---|
| `NET_HTTP_GET` | `axios.get()`, `https.get()` | `requests.get()`, `httpx.get()` |
| `NET_HTTP_POST` | `axios.post()` | `requests.post()` |
| `NET_REQUEST` | `fetch()`, `http.request()` | `urllib.request.urlopen()` |
| `NET_SOCKET` | `new WebSocket()` | `socket.socket()` |

**Risk when unjustified:** Data exfiltration, C2 callbacks, telemetry injection

---

### 📁 FILESYSTEM

Capabilities that read, write, or delete local files.

| Action | APIs (JS) | APIs (Python) |
|---|---|---|
| `FS_READ` | `fs.readFile()`, `fs.readFileSync()` | `open()` |
| `FS_WRITE` | `fs.writeFile()`, `fs.mkdir()` | — |
| `FS_DELETE` | `fs.unlink()`, `fs.rmdir()` | `os.remove()`, `shutil.rmtree()` |

**Risk when unjustified:** Data theft, config tampering, log manipulation

---

### ⚙️ PROCESS

Capabilities that spawn child processes or execute shell commands.

| Action | APIs (JS) | APIs (Python) |
|---|---|---|
| `PROC_EXEC` | `child_process.exec()`, `execSync()` | `os.system()`, `subprocess.run()` |
| `PROC_SPAWN` | `child_process.spawn()` | `subprocess.Popen()` |

**Risk when unjustified:** Remote code execution, privilege escalation, backdoors

---

### 🔑 SECRET

Capabilities that access environment variables or credentials.

| Action | APIs (JS) | APIs (Python) |
|---|---|---|
| `SECRET_READ_ENV` | `process.env.KEY` | `os.environ`, `os.getenv()` |
| `SECRET_READ_CRED` | — | — |

**Risk when unjustified:** API key theft, credential harvesting

---

### 🗄️ DATABASE

Capabilities that connect to or query databases.

| Action | APIs (JS) | APIs (Python) |
|---|---|---|
| `DB_CONNECT` | — | — |
| `DB_QUERY` | — | — |

**Note:** Database detection is currently rule-based for common ORM patterns.

---

### 🔄 RUNTIME

Capabilities that execute dynamic or arbitrary code.

| Action | APIs (JS) | APIs (Python) |
|---|---|---|
| `RUNTIME_EVAL` | `eval()`, `new Function()` | `eval()`, `exec()` |
| `RUNTIME_DYNAMIC_IMPORT` | — | `importlib.import_module()` |

**Risk when unjustified:** Code injection, sandbox escape, unpredictable behavior

---

## Risk Scoring

Each detected capability receives a **risk score** (0.0 – 1.0):

| Verdict | Score Range | Meaning |
|---|---|---|
| `JUSTIFIED` | 0.0 | Capability aligns with intent |
| `CONDITIONALLY_JUSTIFIED` | 0.1 – 0.4 | Permitted but scope exceeds declaration |
| `SUSPICIOUS` | 0.5 – 0.7 | Needs review |
| `UNJUSTIFIED` | 0.75 – 0.95 | Direct policy violation |

High-impact categories (`PROCESS`, `SECRET`, `NETWORK`) receive the maximum score of **0.95** when unjustified.

---

## Adding Custom API Rules

You can extend the taxonomy for custom or proprietary APIs by modifying [`core/taxonomy.py`](https://github.com/ashucfx/scopelock/blob/main/core/taxonomy.py):

```python
# Add to JS_SENSITIVE_APIS or PY_SENSITIVE_APIS
"myCustomFetch": (CapabilityCategory.NETWORK, CapabilityAction.NET_REQUEST, "HIGH"),
"internalExec": (CapabilityCategory.PROCESS, CapabilityAction.PROC_EXEC, "CRITICAL"),
```
