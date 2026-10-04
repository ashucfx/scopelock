# Divergence Scoring

The **Zero-Trust Divergence Engine** computes the **capability divergence set** Δ and assigns risk scores to each finding.

---

## The Formula

```
Δ = C_obs \ C_exp
```

| Symbol | Meaning |
|---|---|
| `C_obs` | Set of capabilities **observed** in code via AST analysis |
| `C_exp` | Set of capabilities **expected** by developer intent (from `ScopePolicy`) |
| `Δ` | **Divergence set** — capabilities in `C_obs` not in `C_exp` |

If `Δ = ∅` (empty), the code has exactly the permissions it needs → **PASSED**  
If `|Δ| > 0`, capability over-reach is detected → **FAILED**

---

## Verdict Tiers

Each finding receives one of five verdicts:

| Verdict | Risk Score | Meaning | Audit Result |
|---|---|---|---|
| `JUSTIFIED` | 0.0 | Capability is authorized by intent | ✅ PASS |
| `CONDITIONALLY_JUSTIFIED` | 0.1–0.4 | Permitted category but conditional | ✅ PASS |
| `SUSPICIOUS` | 0.5–0.65 | Target scope exceeds declared scope | ⚠️ FAIL |
| `UNJUSTIFIED` | 0.75–0.95 | Capability not authorized at all | ❌ FAIL |
| `AMBIGUOUS` | 0.5 | Intent was too vague to evaluate | 🔄 NEEDS_REVIEW |

---

## Risk Score Breakdown

For `UNJUSTIFIED` findings, scores are assigned by category:

| Category | Score | Rationale |
|---|---|---|
| `PROCESS` | **0.95** | Shell execution is highest risk — enables RCE |
| `SECRET` | **0.95** | Credential access enables supply-chain attacks |
| `NETWORK` | **0.95** | Data exfiltration / C2 callbacks |
| `DATABASE` | **0.75** | Data leakage but scope-limited |
| `FILESYSTEM` | **0.75** | Data theft potential |
| `RUNTIME` | **0.75** | Dynamic eval risks |

---

## Final Verdict Logic

```python
violations = [f for f in findings if f.verdict in (UNJUSTIFIED, SUSPICIOUS)]
final_verdict = FAILED if violations else PASSED
```

Both `UNJUSTIFIED` and `SUSPICIOUS` findings count as violations. **Only `JUSTIFIED` findings produce a PASS.**

---

## Reading the JSON Report

```json
{
  "final_verdict": "FAILED",
  "total_violations": 2,
  "findings": [
    {
      "verdict": "JUSTIFIED",
      "risk_score": 0.0,
      "finding": "Justified FILESYSTEM access: 'open()' aligns with stated requirements.",
      "recommendation": "Permission authorized by intent contract."
    },
    {
      "verdict": "UNJUSTIFIED",
      "risk_score": 0.95,
      "finding": "Unjustified NETWORK capability detected. The stated intent does not authorize invoking 'fetch'.",
      "recommendation": "Remove or refactor 'fetch' at Line 4, Column 2 before deploying."
    }
  ]
}
```
