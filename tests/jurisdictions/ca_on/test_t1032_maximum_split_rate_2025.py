"""The 2025 maximum split rate of Form T1032 line 20, `ca/t1032_maximum_split_rate`, checked against
the printed form.

Form T1032 E (25), Step 2, page 2: "Line 20: Maximum rate 50%", applied at line 21 ("Line 19
multiplied by line 20 Maximum split-pension amount"). The printed 50% is the rate, 0.5. The form
states no rounding rule; the product is rounded by the form's own dollars-and-cents line, the
owner's decision, the repo convention. The dataset is the `rate` kind, applied by `core/apply_rate`.

Form T1032 is at https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt
"""

from __future__ import annotations

from decimal import Decimal

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.registry import Namespace

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
RATE_NAME = "ca/t1032_maximum_split_rate"
T1032_TXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1032/t1032-25e.txt"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, whitespace squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    lines = (
        (root / "parameters" / family.removeprefix("ca/") / "2025.yaml").read_text().splitlines()
    )
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return " ".join(" ".join(lines[:first_key]).split())


def test_2025_maximum_split_rate_is_one_half() -> None:
    data = SOURCE.get(RATE_NAME, 2025, RATE)

    assert data.values == Rate(D("0.5"))


def test_2025_maximum_split_rate_cites_form_t1032_line_20() -> None:
    data = SOURCE.get(RATE_NAME, 2025, RATE)

    assert data.sources == (T1032_TXT,)
    header = dataset_header(RATE_NAME)
    assert "Form T1032 E (25)" in header
    assert "Line 20" in header
    assert "Maximum rate 50%" in header


def test_2025_maximum_split_rate_rounds_half_up_to_the_cent() -> None:
    assert SOURCE.get(RATE_NAME, 2025, RATE).rounding == CENT
