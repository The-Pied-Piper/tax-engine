# tax_calculator

A jurisdiction-agnostic personal income tax computation engine. Canada and Ontario
are the bundled pilot jurisdictions. Requires Python 3.12 or newer.

## Development with uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uv sync --extra dev --locked
uv run --extra dev --locked ruff check .
uv run --extra dev --locked ruff format --check .
uv run --extra dev --locked mypy src tests
uv run --extra dev --locked python -m pytest
uv build
```

`uv sync` creates a `.venv` in the repository; manual activation is not needed.
The committed lockfile fixes the development environment's dependency versions.
After intentionally changing dependencies, run `uv lock` and commit the updated
lockfile.

## Development with Python and pip

uv is optional. From the repository root:

```sh
python -m venv .venv
```

Activate the environment:

- Linux/macOS: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Then install, test, and build:

```sh
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy src tests
python -m pytest
python -m build
```

This installs the same declared development extras, but pip does not use
the uv lockfile.

Both build workflows produce a wheel and source distribution in `dist/`.
The distributions include the jurisdiction manifests and parameter YAML files.

CI runs the lint, formatting, type, and test checks on Python 3.12 for pull requests
targeting `main` and pushes to `main`.

The [CRA reference archive](docs/cra-forms-2025/README.md) contains the saved
forms, guides, and source provenance used to verify the Canadian calculations.

## Engine usage

```python
from tax_calculator import build_tax_computation
from tax_calculator.domain.jurisdiction_code import JurisdictionCode

engine = build_tax_computation()
forms = engine.compose(JurisdictionCode("CA-ON"), 2025)
```

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
