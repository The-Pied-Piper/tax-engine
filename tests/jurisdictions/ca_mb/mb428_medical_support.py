"""Support for the per-line tests of the MB428 (2025) medical expense parts, lines 43 to 50.

Each test loads one real part file from the Manitoba manifest folder beside a header and a form
declaration made up here, gives the part's upstream lines as inputs, and reads the line it computes
through the real engine.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path
from textwrap import dedent

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_mb.support import (
    manitoba_capabilities,
    manitoba_kinds,
    manitoba_packages,
    manitoba_parameter_parsers,
    manitoba_units,
)

D = Decimal
MB_PARTS = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025"
FORM_NAME = "ca-mb/mb428_credits"


def compute_line(
    tmp_path: Path,
    part: str,
    inputs: dict[str, str],
    output: str,
    *,
    extra_parts: Sequence[Path] = (),
    part_inputs: dict[str, str] | None = None,
    outputs: tuple[str, ...] = (),
    form_name: str = FORM_NAME,
) -> Decimal:
    """The value of `output` from the real part `part`, given `inputs` (kind identifier to
    amount) as the header's own inputs, after any `extra_parts` composed beside it. `part_inputs`
    are given too but declared by those parts, not by the header."""
    kinds = manitoba_kinds()
    header = (
        "jurisdiction: CA-MB\nversion: 1\nvalid_from_tax_year: 2025\n"
        + "outputs: []\n"
        + "capabilities: []\n"
    )
    # The inputs are the form's own: the form's steps read them, so no other form may hold them.
    form = (
        dedent(f"""\
        form:
          name: {form_name}
          required: true
          exports:
            - {output}
        capabilities: []
        """)
        + ("inputs:\n" if inputs else "")
        + "".join(f"  - name: {name}\n    required: true\n" for name in inputs)
    )
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(header, encoding="utf-8")
    (folder / "01_form.yaml").write_text(form, encoding="utf-8")
    parts = [*extra_parts, MB_PARTS / part]
    for number, path in enumerate(dict.fromkeys(parts), start=2):
        (folder / f"{number:02d}_{path.name}").write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8"
        )
    roots = {**manitoba_packages().roots(), Namespace("ca-mb"): tmp_path}
    service = TaxComputationService(
        YamlJurisdictionSource(roots, kinds, manitoba_units()),
        YamlParameterSource(
            manitoba_packages().roots(), manitoba_parameter_parsers(), manitoba_units()
        ),
        manitoba_capabilities(),
    )
    given = [
        Artifact(kinds.kind(name), D(value))
        for name, value in {**inputs, **(part_inputs or {})}.items()
    ]
    (sheet,) = service.compute(
        TaxCalculationRequest(JurisdictionCode("CA-MB"), 2025, tuple(given))
    )[form_name]
    value = sheet.get(kinds.kind(output)).value
    assert isinstance(value, Decimal)
    return value
