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

For 2026 only, a figure CRA has not yet printed on a form may be calculated, carried forward from 2025, or indexed. This overrides the rule that printed constants are never recomputed, for 2026 files only. Such a file keeps the Provisional line first, followed on the next line by a `# Derivation:` line stating which of the three it is and how the figure was made, for example `# Derivation: thresholds and rates as printed in T4127 Table 8.1; tax_at_start calculated as the cumulative tax on the earlier brackets, rounded half-up to the cent (reproduces the 2025 printed constants).`

## Docstrings

A docstring tells a reader what a module, class or function is and does now.

1. Write in the present tense: one summary line, plus a short paragraph only if the summary is not enough.
2. No change history ("now also", "previously", "replaces"). That belongs in the pull request and in git.
3. No "does not", "no longer" or "removed" sentences about behaviour that is not there. State a limit only if a caller would otherwise be caught out, in one sentence.
4. Do not restate the signature, types or names. Describe what they cannot show: units, rounding, what a blank means, what it raises.
5. Keep it to the summary line plus about 5 lines. A module docstring is 1 to 3 lines. Anything longer is a spec: put it in `docs/` and link it from the docstring.
6. Why a rule exists (a CRA form line, a ruling) goes in a comment or a doc page, not in the docstring.
