"""Shared helpers of the solidarity reduction rule tests: the test header, form part and figures.

The reduction chain consumes four artifacts the solidarity wiring produces (family income, the
maximum before reduction, the QST component amount and the housing count), so the test form
declares the ones the part consumes as inputs. The form part exports the printed amounts and every
figure of the chain that no later step consumes (a form cannot hold an output nothing reads), so
the tests can read any step's figure.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds

FORM = "ca-qc/solidarity_credit"
INPUTS = [
    "ca-qc/solidarity_family_income",
    "ca-qc/solidarity_maximum_before_reduction",
    "ca-qc/solidarity_qst_component_amount",
    "ca-qc/solidarity_housing_received",
]


def _steps() -> list[dict[str, Any]]:
    part = yaml.safe_load((QUEBEC_PARTS / "solidarity_credit_reduction.yaml").read_text("utf-8"))
    steps = part["capabilities"]
    assert isinstance(steps, list)
    return steps


def _consumed() -> set[str]:
    consumed: set[str] = set()
    for step in _steps():
        for value in step["consumes"].values():
            consumed.update(value if isinstance(value, list) else [value])
    return consumed


def solidarity_header() -> str:
    """A test header: the default form exports nothing, and the chain's inputs belong to the form
    that reads them, so the form part declares them."""
    return "jurisdiction: CA-QC\nversion: 1\nvalid_from_tax_year: 2025\noutputs: []\n"


def solidarity_form_part(identifier: str) -> str:
    """The real form part with `identifier` and the unconsumed chain outputs added as exports."""
    form = yaml.safe_load((QUEBEC_PARTS / "solidarity_credit.yaml").read_text("utf-8"))["form"]
    exports = list(form["exports"])
    consumed = _consumed()
    unconsumed = [
        step["produces"]["output"]
        for step in _steps()
        if step["produces"]["output"] not in consumed
    ]
    for name in [identifier, *unconsumed]:
        if name not in exports:
            exports.append(name)
    lines = "".join(f"    - {name}\n" for name in exports)
    names = "".join(
        f"  - name: {name}\n    required: true\n" for name in INPUTS if name in consumed
    )
    return (
        dedent(f"""\
        form:
          name: {FORM}
          required: true
          exports:
        """)
        + lines
        + ("inputs:\n" + names if names else "")
    )


def amounts_form_part() -> str:
    """The real form part with only the printed amounts exported, for the tests that compose the
    amounts part alone (the credit after the reduction is produced by the reduction part)."""
    form = yaml.safe_load((QUEBEC_PARTS / "solidarity_credit.yaml").read_text("utf-8"))["form"]
    exports = [
        name for name in form["exports"] if name != "ca-qc/solidarity_credit_after_reduction"
    ]
    lines = "".join(f"    - {name}\n" for name in exports)
    return f"form:\n  name: {FORM}\n  required: true\n  exports:\n{lines}"


def solidarity_figure(
    take_home_service: TakeHomeService,
    identifier: str,
    income: str,
    maximum: str = "363",
    qst: str = "363",
    housing: int = 0,
) -> Decimal:
    """The figure `identifier` of the reduction chain for the given inputs.

    The defaults are a person who is not alone and neither tenant nor owner: maximum 363 (the QST
    base amount), QST component 363 and no housing component.
    """
    service = take_home_service(
        solidarity_header(),
        solidarity_form_part(identifier),
        "solidarity_credit_amounts.yaml",
        "solidarity_credit_reduction.yaml",
    )
    values: dict[str, Any] = {
        "ca-qc/solidarity_family_income": Decimal(income),
        "ca-qc/solidarity_maximum_before_reduction": Decimal(maximum),
        "ca-qc/solidarity_qst_component_amount": Decimal(qst),
        "ca-qc/solidarity_housing_received": housing,
    }
    given: list[Artifact[Any]] = [
        Artifact(quebec_kinds().kind(name), values[name]) for name in INPUTS if name in _consumed()
    ]
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *given)[FORM]
    figure = sheet.get(quebec_kinds().kind(identifier)).value
    assert isinstance(figure, Decimal)
    return figure
