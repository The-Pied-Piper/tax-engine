import os
import subprocess
import sys
from pathlib import Path

from tax_calculator import build_tax_computation
from tax_calculator.domain.jurisdiction_code import JurisdictionCode


def test_import_does_not_load_http_or_database_dependencies(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    subprocess.run(
        [
            sys.executable,
            "-W",
            "error",
            "-c",
            """
import sys
import tax_calculator

for name in ("connexion", "starlette", "sqlalchemy", "asyncpg"):
    assert name not in sys.modules, name
""",
        ],
        cwd=tmp_path,
        env=environment,
        check=True,
    )


def test_bundled_jurisdiction_data_composes() -> None:
    engine = build_tax_computation()
    forms = engine.compose(JurisdictionCode("CA-ON"), 2025)

    assert len(forms.forms) == 48
    order = forms.form("ca-on/return").composition.order
    assert order
    assert len(order) == len({(type(step), step.consumes, step.produces) for step in order})
