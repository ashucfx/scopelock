# In-Code Intent Annotations

Declare your intent directly inside source code comments using the `@intent:` annotation. ScopeLock automatically extracts these during project scans — no `--prompt` flag required.

## Syntax

=== "JavaScript / TypeScript"

    ```javascript
    // @intent: <your natural language requirement>
    ```

    ```javascript
    /* @intent: <your natural language requirement> */
    ```

=== "Python"

    ```python
    # @intent: <your natural language requirement>
    ```

    ```python
    """@intent: <your natural language requirement>"""
    ```

---

## Where to Place It

Place the `@intent:` annotation in the **first 25 lines** of the file, ideally at the very top:

=== "JavaScript"

    ```javascript title="src/utils/calculator.js"
    // @intent: Local arithmetic calculator — compute price with tax, no network or file access

    function calculateTotal(price, taxRate) {
        return price * (1 + taxRate);
    }

    module.exports = { calculateTotal };
    ```

=== "TypeScript"

    ```typescript title="src/api/weather.ts"
    // @intent: Fetch current weather from OpenWeatherMap API for a given city name

    import axios from 'axios';

    export async function getWeather(city: string): Promise<object> {
        const res = await axios.get(`https://api.openweathermap.org/data/2.5/weather?q=${city}`);
        return res.data;
    }
    ```

=== "Python"

    ```python title="src/data/csv_reader.py"
    # @intent: Read a local CSV file and return rows as a list of dictionaries

    import csv

    def read_csv(filepath: str) -> list[dict]:
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    ```

---

## How ScopeLock Reads It

When you run `scopelock scan-project ./src`, ScopeLock:

1. Scans the first 25 lines of each file for an `@intent:` pattern
2. Extracts the intent text after the colon
3. Passes it to the Intent Decomposer Engine to produce a `ScopePolicy`
4. Compares the policy against observed capabilities

```
[SCAN] src/utils/calculator.js
  Intent found: "Local arithmetic calculator — compute price with tax, no network or file access"
  Policy: NET=DENY, FS=DENY, PROC=DENY
  Observed: [fetch() at L4] → UNJUSTIFIED ❌
```

---

## Priority Order

When multiple intent sources exist, ScopeLock uses this priority:

```
@intent: annotation (highest priority)
    ↓
scopelock.json policy file
    ↓
Inferred from filename (lowest priority)
```

---

## Good Intent Examples

| Use Case | Good `@intent:` |
|---|---|
| Calculator | `Local arithmetic calculator — pure computation, offline only` |
| CSV reader | `Read a local CSV file and return rows as structured data` |
| Weather app | `Fetch live weather from OpenWeatherMap API for a city` |
| Auth module | `Authenticate users via JWT tokens against PostgreSQL database` |
| Markdown formatter | `Format raw text into GitHub Markdown — no external calls needed` |
| Shell script runner | `Execute shell commands to manage system processes` |

---

## Bad Intent Examples (Too Vague)

!!! warning "Avoid ambiguous intent"
    These trigger ScopeLock's **ambiguity detection** and may force NEEDS_REVIEW status:

    - ❌ `"General utility tool"`
    - ❌ `"Manage my stuff"`
    - ❌ `"System tool"`
    - ❌ `"Do whatever is needed"`

    **Be specific** about what the module does and what it accesses.
