# Contributing to ScopeLock

Thank you for your interest in contributing! ScopeLock is an open-source research project and welcomes contributions of all kinds.

## Getting Started

```bash
# Fork and clone
git clone https://github.com/ashucfx/scopelock.git
cd scopelock

# Set up development environment
pip install -e ".[dev]"

# Run tests to verify your setup
pytest tests/ -v
```

## Areas for Contribution

### 🌍 New Language Support

Add a new language visitor following the pattern in [`scanner/py_visitor.py`](https://github.com/ashucfx/scopelock/blob/main/scanner/py_visitor.py):

1. Install the Tree-sitter grammar: `pip install tree-sitter-java`
2. Create `scanner/java_visitor.py`
3. Add API rules to `core/taxonomy.py`
4. Register the new language in `scanner/engine.py`
5. Add tests in `tests/test_ast_java.py`

### 🧪 Benchmark Dataset

Add new test programs to [`benchmarks/dataset.py`](https://github.com/ashucfx/scopelock/blob/main/benchmarks/dataset.py):

```python
BenchmarkCase(
    id="my-new-test",
    prompt="Your natural language prompt",
    code="""
    // Your test code here
    """,
    lang="js",
    expected_verdict=AuditVerdict.FAILED,
    expected_categories={CapabilityCategory.NETWORK},
    description="What this test case validates"
)
```

### 📖 Documentation

Improve any page in [`docs-site/docs/`](https://github.com/ashucfx/scopelock/tree/main/docs-site/docs).

### 🖥️ VS Code Extension

The VS Code extension is the highest-priority feature. If you have TypeScript/VS Code extension development experience, please open an issue to coordinate!

## Development Workflow

```bash
# Create a feature branch
git checkout -b feat/your-feature-name

# Make your changes
# ...

# Lint
ruff check .

# Test
pytest tests/ -v

# Commit
git commit -m "feat: add Java language support"

# Push and open a PR
git push origin feat/your-feature-name
```

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|---|---|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `test:` | Adding or fixing tests |
| `refactor:` | Code restructuring |
| `perf:` | Performance improvement |
| `chore:` | Build/tooling changes |

## Code Style

- Python: **ruff** (configured in `pyproject.toml`)
- Line length: **100 characters**
- Type hints: **required** on all public functions
- Docstrings: **required** on all public classes and methods

## License

By contributing, you agree your contributions will be licensed under the [Apache 2.0 License](https://github.com/ashucfx/scopelock/blob/main/LICENSE).
