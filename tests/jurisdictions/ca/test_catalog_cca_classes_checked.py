"""The `_checked` record lists of the CCA table's Area A rows, Forms T776, T2125, T2042 and T2121:
the rows that passed `ca/cca_vehicle_additions_checks` (a Class 10.1 vehicle's additions are not
more than its limit with tax), passed on unchanged, one list for each business type and for rental.

Each kind holds the fields of its `classes` list in the same order (the checks pass the rows on
unchanged, and the vehicle fields stay until the proceeds adjustment), is a record list, and is
registered under its identifier in the snapshot (`catalog_snapshot.py`).
"""

from __future__ import annotations

import ast
from pathlib import Path

import tax_engine.jurisdictions.ca.catalog


def squashed(text: str) -> str:
    return " ".join(text.split())


def docstring_of(identifier: str) -> str:
    """The string right after the declaration of the kind `identifier` in a catalog module (its
    name is a constant of the declaration's call, which may take the catalog first)."""
    folder = Path(tax_engine.jurisdictions.ca.catalog.__file__).parent
    for path in sorted(folder.glob("*.py")):
        body = ast.parse(path.read_text()).body
        for statement, following in zip(body, body[1:], strict=False):
            if not (isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call)):
                continue
            constants = [
                each.value for each in statement.value.args if isinstance(each, ast.Constant)
            ]
            if not (
                identifier.rpartition("/")[2] in constants
                and isinstance(following, ast.Expr)
                and isinstance(following.value, ast.Constant)
            ):
                continue
            return str(following.value.value)
    raise AssertionError(f"no declaration of {identifier!r} followed by a docstring")
