"""YamlJurisdictionSource: a manifest imports forms of another package by name (#618).

A manifest may carry `imports:`, a list of form identifiers `<ns>/<local_id>`. The parts of an
imported form live in `<package dir of ns>/forms/<local_id>/` (every `*.yaml` / `*.yml`, sorted,
recursively), not under `manifests/`. They load with the importing manifest's own parts: `forms`
runs the default form, then the imported forms in `imports` order, then the manifest's own.

An imported part may carry only `form` and `capabilities`, and its `form.name` is the imported
identifier. A form that declares `exports` may also declare `supplies`, a mapping from a neutral
derived identifier (`ex/provincial_tax.amount`) to one of its own exports, so an imported form
reads a figure each importing manifest supplies under that name. Names are made up: the package
`ex` holds the shared form `ex/federal`, `ex-on` and `ex-ab` are two provinces importing it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any, ClassVar

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import Capability, CapabilityRegistry, CapabilityResult
from tax_engine.domain.errors import InvalidManifestError, NotFoundError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.manifest import Manifest
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.core.capabilities.record_total import RecordTotal
from tests.adapters.outbound.test_yaml_jurisdictions import manifest_kinds, write

EX_ON = JurisdictionCode("EX-ON")
EX_AB = JurisdictionCode("EX-AB")
D = Decimal
NEUTRAL = "ex/provincial_tax.amount"


def package_roots(directory: Path) -> Mapping[Namespace, Path]:
    return {
        Namespace("ex"): directory / "ex",
        Namespace("ex-on"): directory / "ex-on",
        Namespace("ex-ab"): directory / "ex-ab",
    }


def source(directory: Path) -> YamlJurisdictionSource:
    return YamlJurisdictionSource(package_roots(directory), manifest_kinds())


def header(code: str, imports: str = "[ex/federal]") -> str:
    return f"""\
jurisdiction: {code}
version: 1
valid_from_tax_year: 2025
inputs: [{{name: ex/income, required: true}}]
outputs: [ex/income]
imports: {imports}
"""


FEDERAL = """\
form:
  name: ex/federal
  required: true
  exports: [ex/federal_total]
capabilities:
  - name: core/record_total
    consumes: {records: ex/provincial_tax.amount}
    produces: {output: ex/federal_total}
"""

FEDERAL_NAME_ONLY = """\
form:
  name: ex/federal
capabilities:
  - {name: ex/extra, produces: {output: ex/federal_total}}
"""


def province_form(code: str, capability: str = "ex/half") -> str:
    """The province's form: its tax from the income, supplied under the neutral name."""
    return f"""\
form:
  name: {code}/levy
  required: true
  exports: [{code}/tax]
  supplies: {{{NEUTRAL}: {code}/tax}}
capabilities:
  - name: {capability}
    consumes: {{source: ex/income}}
    produces: {{target: {code}/tax}}
"""


def write_federal(directory: Path, parts: Mapping[str, str] | None = None) -> None:
    for name, content in (parts or {"00-federal.yaml": FEDERAL}).items():
        write(directory, f"ex/forms/federal/{name}", content)


def write_province(
    directory: Path,
    code: str = "ex-on",
    *,
    head: str | None = None,
    form: str | None = None,
    extra: Mapping[str, str] | None = None,
) -> None:
    folder = f"{code}/manifests/v1"
    write(directory, f"{folder}/00-header.yaml", head or header(code.upper()))
    write(directory, f"{folder}/01-levy.yaml", form or province_form(code))
    for name, content in (extra or {}).items():
        write(directory, f"{folder}/{name}", content)


def manifest_of(directory: Path, code: JurisdictionCode = EX_ON) -> Manifest:
    (manifest,) = source(directory).get_jurisdiction(code).manifests
    return manifest


def names(manifest: Manifest) -> list[str]:
    return [form.name for form in manifest.forms]


# --- an `imports:` manifest loads the named forms' parts plus its own ---------------------------


def test_a_manifest_loads_the_imported_forms_parts_with_its_own(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path)

    manifest = manifest_of(tmp_path)

    federal = next(form for form in manifest.forms if form.name == "ex/federal")
    assert federal.exports == ("ex/federal_total",)
    assert [c.name for c in federal.capabilities] == ["core/record_total"]
    assert "ex-on/levy" in names(manifest)


def test_the_forms_run_default_then_imported_in_imports_order_then_own(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write(
        tmp_path,
        "ex/forms/aid/00-aid.yaml",
        "form: {name: ex/aid, required: true, exports: [ex/aid_total]}\n"
        "capabilities:\n  - {name: ex/c, produces: {output: ex/aid_total}}\n",
    )
    write_province(tmp_path, head=header("EX-ON", "[ex/federal, ex/aid]"))
    write(tmp_path, "ex-on/manifests/v1/02-zz.yaml", province_form("ex-on").replace("levy", "aa"))

    assert names(manifest_of(tmp_path)) == [
        "ex-on/return",
        "ex/federal",
        "ex/aid",
        "ex-on/levy",
        "ex-on/aa",
    ]


def test_imports_order_decides_not_the_alphabet(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write(
        tmp_path,
        "ex/forms/aid/00-aid.yaml",
        "form: {name: ex/aid, required: true, exports: [ex/aid_total]}\n"
        "capabilities:\n  - {name: ex/c, produces: {output: ex/aid_total}}\n",
    )
    write_province(tmp_path, head=header("EX-ON", "[ex/federal, ex/aid]"))
    first = names(manifest_of(tmp_path))
    write_province(tmp_path, head=header("EX-ON", "[ex/aid, ex/federal]"))

    assert first[1:3] == ["ex/federal", "ex/aid"]
    assert names(manifest_of(tmp_path))[1:3] == ["ex/aid", "ex/federal"]


def test_an_imported_form_spans_parts_read_in_sorted_order_in_nested_folders(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path, {"00-federal.yaml": FEDERAL, "sub/01-more.yml": FEDERAL_NAME_ONLY})
    write_province(tmp_path)

    federal = next(form for form in manifest_of(tmp_path).forms if form.name == "ex/federal")

    assert [c.name for c in federal.capabilities] == ["core/record_total", "ex/extra"]


def test_imports_in_two_parts_are_concatenated_in_part_order(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write(
        tmp_path,
        "ex/forms/aid/00-aid.yaml",
        "form: {name: ex/aid, required: true, exports: [ex/aid_total]}\n"
        "capabilities:\n  - {name: ex/c, produces: {output: ex/aid_total}}\n",
    )
    write_province(tmp_path, extra={"02-more.yaml": "imports: [ex/aid]\n"})

    assert names(manifest_of(tmp_path))[1:3] == ["ex/federal", "ex/aid"]


def test_a_whole_file_manifest_may_import(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write(
        tmp_path,
        "ex-on/manifests/v1.yaml",
        header("EX-ON") + "capabilities: []\n",
    )

    assert "ex/federal" in names(manifest_of(tmp_path))


def test_a_manifest_without_imports_loads_as_before(tmp_path: Path) -> None:
    write_province(tmp_path, head=header("EX-ON").replace("imports: [ex/federal]\n", ""))

    assert names(manifest_of(tmp_path)) == ["ex-on/return", "ex-on/levy"]


# --- two provinces import the same form -----------------------------------------------------------


def test_two_provinces_importing_the_same_form_both_load(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, "ex-on")
    write_province(tmp_path, "ex-ab")

    on = manifest_of(tmp_path, EX_ON)
    ab = manifest_of(tmp_path, EX_AB)

    assert "ex/federal" in names(on)
    assert "ex/federal" in names(ab)
    assert "ex-on/levy" in names(on)
    assert "ex-ab/levy" in names(ab)


# --- rejections ----------------------------------------------------------------------------------


def test_an_unknown_import_is_rejected_naming_it_and_the_manifest(tmp_path: Path) -> None:
    write_province(tmp_path, head=header("EX-ON", "[ex/missing]"))

    with pytest.raises(InvalidManifestError, match="ex/missing") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "00-header.yaml" in str(caught.value)


def test_an_import_from_a_namespace_without_a_package_is_rejected(tmp_path: Path) -> None:
    write_province(tmp_path, head=header("EX-ON", "[zz/federal]"))

    with pytest.raises(InvalidManifestError, match="zz/federal"):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_an_import_whose_folder_has_no_parts_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "ex" / "forms" / "federal").mkdir(parents=True)
    write_province(tmp_path)

    with pytest.raises(InvalidManifestError, match="ex/federal"):
        source(tmp_path).get_jurisdiction(EX_ON)


@pytest.mark.parametrize(
    "key",
    [
        "jurisdiction: EX-ON\n",
        "version: 1\n",
        "valid_from_tax_year: 2025\n",
        "title: Federal\n",
        "inputs: [{name: ex/income, required: true}]\n",
        "outputs: [ex/federal_total]\n",
        "imports: [ex/other]\n",
    ],
    ids=["jurisdiction", "version", "valid_from_tax_year", "title", "inputs", "outputs", "imports"],
)
def test_an_imported_part_carrying_a_manifest_key_is_rejected_naming_part_and_key(
    tmp_path: Path, key: str
) -> None:
    write_federal(tmp_path, {"00-federal.yaml": FEDERAL, "01-bad.yaml": FEDERAL_NAME_ONLY + key})
    write_province(tmp_path)

    with pytest.raises(InvalidManifestError, match=key.split(":")[0]) as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "01-bad.yaml" in str(caught.value)


def test_an_imported_part_without_a_form_block_is_rejected_naming_the_part(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path, {"00-federal.yaml": FEDERAL, "01-bare.yaml": "capabilities: []\n"})
    write_province(tmp_path)

    with pytest.raises(InvalidManifestError, match="form") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "01-bare.yaml" in str(caught.value)


def test_a_form_listed_twice_in_imports_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, head=header("EX-ON", "[ex/federal, ex/federal]"))

    with pytest.raises(InvalidManifestError, match="ex/federal.*more than once"):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_a_form_listed_in_two_parts_imports_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, extra={"02-more.yaml": "imports: [ex/federal]\n"})

    with pytest.raises(InvalidManifestError, match="ex/federal.*more than once"):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_an_own_part_naming_an_imported_form_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, extra={"02-clash.yaml": FEDERAL_NAME_ONLY})

    with pytest.raises(InvalidManifestError, match="ex/federal") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "02-clash.yaml" in str(caught.value)


def test_an_imported_folder_whose_part_names_another_form_is_rejected(tmp_path: Path) -> None:
    write_federal(
        tmp_path,
        {
            "00-federal.yaml": FEDERAL,
            "01-other.yaml": FEDERAL_NAME_ONLY.replace("federal", "other"),
        },
    )
    write_province(tmp_path)

    with pytest.raises(InvalidManifestError, match="ex/other") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "01-other.yaml" in str(caught.value)


@pytest.mark.parametrize("value", ["ex_federal", "federal", "ex/Federal"])
def test_an_import_that_is_not_a_form_identifier_is_rejected(tmp_path: Path, value: str) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, head=header("EX-ON", f"[{value}]"))

    with pytest.raises(InvalidManifestError, match=re.escape(value)):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_imports_that_is_not_a_list_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, head=header("EX-ON", "ex/federal"))

    with pytest.raises(InvalidManifestError, match="imports must be a list"):
        source(tmp_path).get_jurisdiction(EX_ON)


# --- supplies ------------------------------------------------------------------------------------


def test_the_supplied_neutral_kind_is_one_the_importing_manifest_can_read(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path)

    manifest = manifest_of(tmp_path)
    kind = manifest.kinds.kind(NEUTRAL)

    assert kind.identifier == NEUTRAL
    levy = next(form for form in manifest.forms if form.name == "ex-on/levy")
    assert dict(levy.supplies) == {NEUTRAL: "ex-on/tax"}


def test_the_neutral_kind_of_each_province_has_that_provinces_export_as_its_field(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, "ex-on")
    write_province(tmp_path, "ex-ab")

    on = manifest_of(tmp_path, EX_ON).kinds.kind(NEUTRAL)
    ab = manifest_of(tmp_path, EX_AB).kinds.kind(NEUTRAL)

    assert [field.identifier for field in on.fields] == ["ex-on/tax"]  # type: ignore[attr-defined]
    assert [field.identifier for field in ab.fields] == ["ex-ab/tax"]  # type: ignore[attr-defined]


def test_supplies_without_exports_in_the_same_part_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(
        tmp_path,
        form=f"form:\n  name: ex-on/levy\n  supplies: {{{NEUTRAL}: ex-on/tax}}\n",
    )

    with pytest.raises(InvalidManifestError, match="supplies.*exports|exports.*supplies") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "01-levy.yaml" in str(caught.value)


def test_a_supplied_export_that_is_not_a_record_field_kind_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    text = province_form("ex-on").replace("exports: [ex-on/tax]", "exports: [ex/note]")
    write_province(tmp_path, form=text.replace(f"{NEUTRAL}: ex-on/tax", f"{NEUTRAL}: ex/note"))

    with pytest.raises(InvalidManifestError, match="ex/note") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "supplies" in str(caught.value)


def test_a_supplied_figure_that_is_not_an_export_of_the_form_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    text = province_form("ex-on").replace(f"{NEUTRAL}: ex-on/tax", f"{NEUTRAL}: ex-on/other")
    write_province(tmp_path, form=text)

    with pytest.raises(InvalidManifestError, match="ex-on/other"):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_a_neutral_identifier_supplied_by_two_forms_is_rejected(tmp_path: Path) -> None:
    write_federal(tmp_path)
    second = province_form("ex-on").replace("levy", "second").replace("ex-on/tax", "ex-on/tax2")
    write_province(tmp_path, extra={"02-second.yaml": second})

    with pytest.raises(InvalidManifestError, match="ex/provincial_tax.amount") as caught:
        source(tmp_path).get_jurisdiction(EX_ON)

    assert "02-second.yaml" in str(caught.value)


def test_a_neutral_identifier_that_clashes_with_a_real_derived_kind_is_rejected(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path)
    clash = province_form("ex-on").replace(NEUTRAL, "ex/federal.federal_total")
    write_province(tmp_path, form=clash)

    with pytest.raises(InvalidManifestError, match="ex/federal.federal_total"):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_a_province_that_imports_the_form_without_supplying_the_figure_is_refused(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path)
    # a form without `supplies`: the same part with the key removed
    plain = "\n".join(
        line for line in province_form("ex-on").splitlines() if "supplies" not in line
    )
    write_province(tmp_path, form=plain + "\n")

    with pytest.raises(
        InvalidManifestError,
        match=r"form 'ex/federal': needs 'ex/provincial_tax\.amount', "
        r"which no form of this manifest supplies",
    ):
        source(tmp_path).get_jurisdiction(EX_ON)


def test_one_province_not_supplying_does_not_stop_the_other_from_computing(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, "ex-on")
    plain = "\n".join(
        line for line in province_form("ex-ab").splitlines() if "supplies" not in line
    )
    write_province(tmp_path, "ex-ab", form=plain + "\n")

    assert "ex/federal" in names(manifest_of(tmp_path, EX_ON))
    with pytest.raises(InvalidManifestError, match="ex/federal.*no form of this manifest"):
        source(tmp_path).get_jurisdiction(EX_AB)


# --- end to end: two provinces, one federal form -------------------------------------------------


class Half(Capability):
    """Produces `target` as half of `source`."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"target": Decimal}

    def __init__(self, source: ArtifactKind[Decimal], target: ArtifactKind[Decimal]) -> None:
        super().__init__(source=source, target=target)
        self._source, self._target = source, target

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._source).value / 2
        return CapabilityResult(outputs=(Artifact(self._target, value),), trace=())


class Third(Half):
    """Produces `target` as a third of `source`, to the cent."""

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = (self._input(inputs, self._source).value / 3).quantize(D("0.01"))
        return CapabilityResult(outputs=(Artifact(self._target, value),), trace=())


class NoParameters:
    def get[T](self, family: str, tax_year: int, kind: ParameterKind[T]) -> ParameterDataset[T]:
        raise NotFoundError(f"no {family} dataset for tax year {tax_year}")


def service(directory: Path) -> TaxComputationService:
    capabilities = CapabilityRegistry()
    capabilities.register("core/record_total", RecordTotal)
    capabilities.register("ex/half", Half)
    capabilities.register("ex/third", Third)
    return TaxComputationService(source(directory), NoParameters(), capabilities)


def federal_total(directory: Path, code: JurisdictionCode, income: str) -> Decimal:
    worksheets = service(directory).compute(
        code, 2025, Artifact(AmountKind("ex/income"), D(income))
    )
    (sheet,) = worksheets["ex/federal"]
    total: Decimal = sheet.get(AmountKind("ex/federal_total")).value
    return total


def test_two_provinces_compute_the_one_federal_form_from_their_own_figure(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path, "ex-on")
    write_province(tmp_path, "ex-ab", form=province_form("ex-ab", "ex/third"))

    assert federal_total(tmp_path, EX_ON, "1000") == D("500")
    assert federal_total(tmp_path, EX_AB, "1000") == D("333.33")
