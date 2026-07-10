# Contributing

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Checks

```bash
pytest -q
```

## Guidelines

- Keep APIs small and explicit.
- Add tests for new behavior.
- Prefer deterministic simulations (set seeds).
