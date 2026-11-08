# Contributing

## Development with uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```sh
uv sync --extra dev --locked
uv run --extra dev --locked ruff check .
uv run --extra dev --locked ruff format --check .
uv run --extra dev --locked mypy src tests
uv run --extra dev --locked lint-imports
uv run --extra dev --locked python -m pytest
uv build
```

`uv sync` creates a `.venv` in the repository; manual activation is not needed.
The committed lockfile fixes the development environment's dependency versions.
After intentionally changing dependencies, run `uv lock` and commit the updated lockfile.

## Development with Python and pip

```sh
python -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy src tests
lint-imports
python -m pytest
python -m build
```

pip does not use the uv lockfile. Both build workflows produce a wheel and source distribution in `dist/`, including the jurisdiction manifests and parameter YAML files.

CI runs lint, formatting, type and test checks on Python 3.12 for pull requests targeting `main` and pushes to `main`.

## Provisional 2026 datasets

A 2026 dataset sourced from CRA's T4127 payroll formulas, before CRA publishes the 2026 form text, starts with this exact line:

`# Provisional: taken from T4127 (Jan 2026); to be confirmed against the 2026 form text when CRA publishes it.`

Remove the line in the pull request that confirms the figure against the form. Open items are found with `grep -rl "Provisional:" src/`.

## CRA reference archive

The [CRA reference archive](docs/cra-forms-2025/README.md) holds the saved forms, guides and source provenance used to verify the Canadian calculations.
