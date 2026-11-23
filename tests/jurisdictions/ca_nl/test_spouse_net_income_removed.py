"""NL428 (2025) spouse net income removed (#1894, owner ruling 23 Nov 2026).

The take-home is a single filer's, so the spouse's net income typed twice on NL428 (line 19, read
by line 20, and line 88 of column 2, read by lines 90 to 92 of column 2) is no longer an input,
as Quebec's spouse line 275 was removed in #1925. Nothing keeps a printed blank or a note: the
lines that read it are removed (line 20 and its datasets, column 2 of lines 88 to 92, line 93) and
their readers read the figure for the filer alone (line 25 sums lines 16, 17, 23 and 24; line 23 is
the lesser of the difference and the printed maximum; lines 93 and 99 are copies of line 92 of
column 1, which line 101 reads). The other spouse inputs (lines 46, 86 and 96) are not part of this
ruling and are unchanged.

The figures of a salary-only return are unchanged by the removal: the Form NL428 line 105 tests and
`test_registered.py` already pin them, and are not repeated here.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_nl
from tests.jurisdictions.ca_nl.support import newfoundland_kinds

ROOT = Path(tax_engine.jurisdictions.ca_nl.__file__).parent
MANIFESTS = ROOT / "manifests" / "2025"

SPOUSE_NET_INCOME_INPUTS = (
    "ca-nl/nl428_spouse_net_income_line_19",
    "ca-nl/nl428_spouse_net_income_line_88",
)
# The kinds only the spouse's lines produced or read; every one has gone with its step.
REMOVED_KINDS = (
    *SPOUSE_NET_INCOME_INPUTS,
    "ca-nl/nl428_spouse_amount_before_maximum_line_20",
    "ca-nl/nl428_spouse_amount_line_20",
    "ca-nl/spouse_amount_base",
    "ca-nl/spouse_amount_maximum",
    "ca-nl/nl428_eligible_dependant_amount_before_check_line_23",
    "ca-nl/nl428_eligible_dependant_amount_most_line_23",
    "ca-nl/nl428_spouse_family_income_line_90",
    "ca-nl/nl428_spouse_family_income_less_uccb_rdsp_line_92",
    "ca-nl/nl428_adjusted_family_income_line_93",
    "ca-nl/nl428_spouse_uccb_and_rdsp_repayment_line_89",
    "ca-nl/nl428_spouse_uccb_rdsp_income_line_91",
)
REMOVED_PARTS = (
    "nl428_credits_line_19_input.yaml",
    "nl428_credits_line_20.yaml",
    "nl428_line_88_column_2_input.yaml",
    "nl428_line_89_column_2_input.yaml",
    "nl428_line_90_column_2.yaml",
    "nl428_line_91_column_2_input.yaml",
    "nl428_line_92_column_2.yaml",
    "nl428_line_93.yaml",
)
REMOVED_DATASETS = ("spouse_amount_base", "spouse_amount_maximum", "eligible_dependant_spouse_gate")


def _declared_inputs() -> list[str]:
    names: list[str] = []
    for part in sorted(MANIFESTS.glob("*.yaml")):
        text = yaml.safe_load(part.read_text(encoding="utf-8"))
        if isinstance(text, dict):
            names.extend(item["name"] for item in text.get("inputs", ()))
    return names


def test_neither_spouse_net_income_is_an_input_of_any_part() -> None:
    declared = _declared_inputs()

    assert declared
    for name in SPOUSE_NET_INCOME_INPUTS:
        assert name not in declared


def test_the_parts_that_held_or_read_only_the_spouse_lines_are_gone() -> None:
    assert [name for name in REMOVED_PARTS if (MANIFESTS / name).exists()] == []


def test_no_part_names_a_removed_kind() -> None:
    text = "\n".join(part.read_text(encoding="utf-8") for part in MANIFESTS.glob("*.yaml"))

    assert [name for name in REMOVED_KINDS if name in text] == []


def test_the_removed_kinds_are_no_longer_registered() -> None:
    registered = newfoundland_kinds().identifiers()

    assert [name for name in REMOVED_KINDS if name in registered] == []


def test_the_datasets_only_the_spouse_amount_and_its_gate_read_are_gone() -> None:
    assert [name for name in REMOVED_DATASETS if (ROOT / "parameters" / name).exists()] == []
