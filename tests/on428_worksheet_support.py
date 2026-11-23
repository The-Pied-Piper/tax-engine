"""Test support: one part of Worksheet ON428 (ON428 line 72), run through the real engine.

Each part reads figures other parts produce, so a test declares them as required inputs of its own
form, loads the real part file of the take-home folder beside them, and reads the part's output.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import yaml

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_on.conftest import ONTARIO_PARTS, TakeHomeService
from tests.kinds import bundled_kinds

CODE = JurisdictionCode("CA-ON")
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: []
capabilities: []
"""


def steps(part: str) -> list[dict[str, Any]]:
    """The capability steps of the real Ontario part file `part`, which must declare no input."""
    loaded = yaml.safe_load((ONTARIO_PARTS / part).read_text(encoding="utf-8"))
    assert loaded["form"] == {"name": "ca-on/on428"}
    assert "inputs" not in loaded
    return list(loaded["capabilities"])


def figure(
    take_home_service: TakeHomeService, part: str, output: str, given: dict[str, str]
) -> Decimal:
    """The figure `output` of the real part `part`, with each identifier of `given` declared as a
    required input and given its amount."""
    inputs = "".join(f"  - name: {name}\n    required: true\n" for name in given)
    form = (
        "form:\n  name: ca-on/on428\n  required: true\n  exports:\n"
        f"    - {output}\ninputs:\n{inputs}capabilities: []\n"
    )
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(name), Decimal(value)) for name, value in given.items()]
    (sheet,) = take_home_service(HEADER, form, part).compute(
        TaxCalculationRequest(CODE, 2025, tuple(starting))
    )["ca-on/on428"]
    value = sheet.get(kinds.kind(output)).value
    assert isinstance(value, Decimal)
    return value
