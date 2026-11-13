"""YamlJurisdictionSource: an `imports` entry may read other dataset families than its form's own.

An entry is a form identifier, or a mapping of `form` and `datasets`, from a family the imported
form reads to the family to read instead. Only the parameters of the form's selections change, in
the importing manifest alone; the form's files are shared. Names are made up: the package `ex`
holds the shared form `ex/benefit`, which reads the credit family `ex/base`; `ex-ab` reads
`ex-ab/base` in its place.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import InvalidManifestError, InvalidParameterDataError, NotFoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.core.capabilities.credit_amount import CreditAmount
from tax_engine.registrations import parameter_parsers
from tests.adapters.outbound.test_yaml_imports import (
    EX_AB,
    EX_ON,
    D,
    Half,
    header,
    manifest_of,
    names,
    package_roots,
    province_form,
    source,
    write_province,
)
from tests.adapters.outbound.test_yaml_jurisdictions import write

BENEFIT = """\
form:
  name: ex/benefit
  required: true
  exports: [ex/base_amount]
capabilities:
  - name: core/credit_amount
    params: {amount: ex/base}
    produces: {output: ex/base_amount}
"""
FEDERAL_STUB = """\
form: {name: ex/federal, required: true, exports: [ex/federal_total]}
capabilities:
  - {name: ex/c, produces: {output: ex/federal_total}}
"""


def head(imports: str) -> str:
    return header("EX-ON", imports)


def write_benefit(directory: Path) -> None:
    write(directory, "ex/forms/benefit/00-benefit.yaml", BENEFIT)


def province(directory: Path, imports: str, code: str = "ex-on") -> None:
    write_province(directory, code, head=header(code.upper(), imports), form=province_form(code))


def params_of(directory: Path, code: JurisdictionCode = EX_ON) -> dict[str, str]:
    benefit = next(f for f in manifest_of(directory, code).forms if f.name == "ex/benefit")
    (selection,) = benefit.capabilities
    return dict(selection.params)


REBOUND = "[{form: ex/benefit, datasets: {ex/base: ex-ab/base}}]"


def test_an_entry_with_only_a_form_is_the_bare_name(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, "[{form: ex/benefit}]")

    assert params_of(tmp_path) == {"amount": "ex/base"}


def test_a_rebind_replaces_the_family_in_the_forms_params_and_nothing_else(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, REBOUND)

    manifest = manifest_of(tmp_path)
    benefit = next(f for f in manifest.forms if f.name == "ex/benefit")
    (selection,) = benefit.capabilities
    assert dict(selection.params) == {"amount": "ex-ab/base"}
    assert dict(selection.produces) == {"output": "ex/base_amount"}
    assert benefit.exports == ("ex/base_amount",)


def test_a_rebind_applies_to_the_importing_manifest_alone(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, "[ex/benefit]", "ex-on")
    province(tmp_path, REBOUND, "ex-ab")

    assert params_of(tmp_path, EX_ON) == {"amount": "ex/base"}
    assert params_of(tmp_path, EX_AB) == {"amount": "ex-ab/base"}


def test_a_rebind_in_a_part_applies_like_one_in_the_header(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    write_province(
        tmp_path,
        head=head("[]").replace("imports: []\n", ""),
        extra={"02-imports.yaml": f"imports: {REBOUND}\n"},
    )

    assert params_of(tmp_path) == {"amount": "ex-ab/base"}


def test_a_rebind_of_a_family_the_form_does_not_read_is_rejected(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, "[{form: ex/benefit, datasets: {ex/other: ex-ab/other}}]")

    with pytest.raises(InvalidManifestError, match=r"imports 'ex/benefit'.*'ex/other'.*no part"):
        source(tmp_path).get_jurisdiction(EX_ON)


@pytest.mark.parametrize(
    "entry",
    [
        "{form: ex/benefit, datasets: {}}",
        "{form: ex/benefit, datasets: {ex/base: bad}}",
        "{form: ex/benefit, rebind: {ex/base: ex-ab/base}}",
        "{datasets: {ex/base: ex-ab/base}}",
    ],
    ids=["empty", "target not an identifier", "unknown key", "no form"],
)
def test_a_malformed_entry_is_rejected(tmp_path: Path, entry: str) -> None:
    write_benefit(tmp_path)
    province(tmp_path, f"[{entry}]")

    with pytest.raises(InvalidManifestError):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_rebinds_are_not_chained_each_family_is_swapped_once(tmp_path: Path) -> None:
    two_steps = BENEFIT.replace(
        "exports: [ex/base_amount]", "exports: [ex/base_amount, ex/second_amount]"
    )
    two_steps += (
        "  - name: core/credit_amount\n"
        "    params: {amount: ex/second}\n"
        "    produces: {output: ex/second_amount}\n"
    )
    write(tmp_path, "ex/forms/benefit/00-benefit.yaml", two_steps)
    province(tmp_path, "[{form: ex/benefit, datasets: {ex/base: ex/second, ex/second: ex/third}}]")

    benefit = next(f for f in manifest_of(tmp_path).forms if f.name == "ex/benefit")

    assert [dict(c.params) for c in benefit.capabilities] == [
        {"amount": "ex/second"},
        {"amount": "ex/third"},
    ]


def test_a_form_listed_bare_and_with_a_rebind_is_rejected(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, "[ex/benefit, {form: ex/benefit, datasets: {ex/base: ex-ab/base}}]")

    with pytest.raises(InvalidManifestError, match="ex/benefit.*more than once"):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_names_and_order_of_forms_do_not_change_with_a_rebind(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    write(tmp_path, "ex/forms/federal/00-federal.yaml", FEDERAL_STUB)
    province(tmp_path, f"[ex/federal, {REBOUND[1:-1]}]")

    assert names(manifest_of(tmp_path)) == [
        "ex-on/return",
        "ex/federal",
        "ex/benefit",
        "ex-on/levy",
    ]


# --- end to end: the dataset a province reads is its own --------------------------------------


def credit_file(directory: Path, family: str, amount: str, kind: str = "credit") -> None:
    """A 2025 dataset of `family` under its package; `kind` other than credit holds a rate."""
    namespace, _, rest = family.partition("/")
    value = f'amount: "{amount}"' if kind == "credit" else f'rate: "{amount}"'
    write(
        directory,
        f"{namespace}/parameters/{rest}/2025.yaml",
        f"family: {family}\ntax_year: 2025\nkind: {kind}\nsources: [https://example.test/form]\n"
        f'rounding: {{increment: "0.01", mode: half_up}}\n{value}\n',
    )


def base_amount(directory: Path, code: JurisdictionCode) -> Decimal:
    capabilities = CapabilityRegistry()
    capabilities.register("core/credit_amount", CreditAmount)
    capabilities.register("ex/half", Half)
    parameters = YamlParameterSource(package_roots(directory), parameter_parsers())
    service = TaxComputationService(source(directory), parameters, capabilities)
    income = Artifact(AmountKind("ex/income"), D("1000"))
    (sheet,) = service.compute(code, 2025, income)["ex/benefit"]
    amount: Decimal = sheet.get(AmountKind("ex/base_amount")).value
    return amount


def test_each_province_reads_its_own_dataset_through_the_one_form(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, "[ex/benefit]", "ex-on")
    province(tmp_path, REBOUND, "ex-ab")
    credit_file(tmp_path, "ex/base", "3000")
    credit_file(tmp_path, "ex-ab/base", "2760")

    assert base_amount(tmp_path, EX_ON) == D("3000")
    assert base_amount(tmp_path, EX_AB) == D("2760")


def test_a_rebind_to_a_family_with_no_dataset_fails_when_composed(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, REBOUND, "ex-ab")
    credit_file(tmp_path, "ex/base", "3000")

    with pytest.raises(NotFoundError, match="ex-ab/base"):
        base_amount(tmp_path, EX_AB)


def test_a_rebind_to_a_family_of_another_kind_fails_when_composed(tmp_path: Path) -> None:
    write_benefit(tmp_path)
    province(tmp_path, REBOUND, "ex-ab")
    credit_file(tmp_path, "ex/base", "3000")
    credit_file(tmp_path, "ex-ab/base", "0.5", kind="rate")

    with pytest.raises(InvalidParameterDataError, match="rate.*credit"):
        base_amount(tmp_path, EX_AB)
