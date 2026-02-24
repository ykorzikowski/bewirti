# Testing

## Prerequisites

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements-dev.txt
```

## Lint

```bash
ruff check .
```

## Type check

```bash
mypy app.py receipt_service.py
```

## Unit tests

```bash
pytest -m "not e2e"
```

## E2E regression tests

```bash
pytest -m e2e
```

The e2e test writes generated artifacts to:

```text
.artifacts/test-outputs/
```

## Coverage XML

```bash
pytest -m "not e2e" --cov=. --cov-report=xml --cov-report=term
```

This creates:

```text
coverage.xml
```
