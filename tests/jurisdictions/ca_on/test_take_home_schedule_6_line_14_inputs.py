"""Schedule 6 (2025) line 14's input, the secondary earner exemption, as the Ontario take-home
manifest part declares it.

Form text (Schedule 6, CRA 5000-s6-25e.txt in docs/cra-forms-2025, lines 229-234): "Line 14: If your
working income (line 5) is less than your eligible spouse's working income, enter whichever is less
from column 1: amount from line 5 or line 12. If your working income (line 5) is equal to or more
than your eligible spouse's working income, enter whichever is less from column 2: amount from line
5 or line 12. (maximum $16,386)" is the line's basis in the take-home part. The take-home filer is
single, with no eligible spouse, so a request that leaves the line out is read as blank, and the
line 15 part reads that blank as 0.

The part is loaded from the test data folder under a test-local header, as the take-home header is
another part's.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds
from tests.kinds import bundled_kinds, non_negative

LINE_14 = "ca/cwb_secondary_earner_exemption"
PRINTED_BASIS = (
    "Line 14: If your working income (line 5) is less than your eligible spouse's working income, "
    "enter whichever is less from column 1: amount from line 5 or line 12. If your working income "
    "(line 5) is equal to or more than your eligible spouse's working income, enter whichever is "
    "less from column 2: amount from line 5 or line 12. (maximum $16,386)"
)
PART = Path(tax_engine.jurisdictions.ca_on.__file__).parent / (
    "manifests/2025/schedule_6_line_14_inputs.yaml"
)
HEADER = """\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [ca/total_income]
capabilities: []
"""


def _manifest(tmp_path: Path) -> Manifest:
    folder = tmp_path / "manifest"
    folder.mkdir()
    (folder / "header.yaml").write_text(HEADER)
    shutil.copy(PART, folder / PART.name)
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)


def test_a_request_that_leaves_out_line_14_is_read_as_blank(tmp_path: Path) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(tmp_path).inputs[LINE_14]
    default = declaration.default_artifact(kinds.kind(LINE_14))
    assert not declaration.required
    assert declaration.basis == PRINTED_BASIS
    assert default is not None and default.is_blank


def test_the_line_14_input_kind_is_registered_and_non_negative() -> None:
    kind = bundled_kinds().kind(LINE_14)

    assert kind.identifier == LINE_14
    assert non_negative(kind) is True
