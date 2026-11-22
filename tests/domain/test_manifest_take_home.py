"""A manifest's take-home declaration names forms, kinds and a salary the manifest has."""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from tax_engine.domain.errors import InvalidManifestError
from tax_engine.domain.take_home import FigureReference, TakeHomeFigures
from tests.manifest_support import real_manifest

ON = real_manifest("CA-ON")


def _declared() -> TakeHomeFigures:
    declared = ON.take_home
    if declared is None:
        raise AssertionError("Ontario declares no take-home figures")
    return declared


DECLARED = _declared()


def _with(**changes: Any) -> TakeHomeFigures:
    return dataclasses.replace(DECLARED, **changes)


def test_the_ontario_declaration_is_the_figures_tax_service_reads() -> None:
    assert [name for name, _ in DECLARED.figures] == [
        "income_tax",
        "cpp_base",
        "cpp_enhanced",
        "cpp2",
        "ei",
    ]
    assert DECLARED.income_tax == FigureReference("ca/t1_tax_and_credits", "ca/total_payable")


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"income_tax": FigureReference("ca-on/nothing", "ca/total_payable")}, "no form"),
        ({"income_tax": FigureReference("ca/t1_tax_and_credits", "ca/nothing")}, "take_home"),
        ({"salary": "ca/nothing"}, "take_home"),
        ({"salary": "ca/yes_or_no_answer_does_not_exist"}, "take_home"),
    ],
)
def test_a_declaration_naming_what_is_missing_is_refused(
    changes: dict[str, object], message: str
) -> None:
    with pytest.raises(InvalidManifestError, match=message):
        dataclasses.replace(ON, take_home=_with(**changes))


def test_a_deduction_named_twice_is_refused() -> None:
    ref = DECLARED.income_tax
    with pytest.raises(InvalidManifestError, match="named twice"):
        _with(deductions=(("ei", ref), ("ei", ref)))
    with pytest.raises(InvalidManifestError, match="named twice"):
        _with(deductions=(("income_tax", ref),))
