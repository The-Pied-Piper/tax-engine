# tax-engine: an open-source income tax calculation engine in Python

[![CI](https://github.com/The-Pied-Piper/tax-engine/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/The-Pied-Piper/tax-engine/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tax-engine.svg)](https://pypi.org/project/tax-engine/)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)

**tax-engine is a personal income tax calculation library where every number is a line on a real tax form, and every result explains itself in a readable trace.**

Tax rules live as data taken as printed from the tax authority's own forms. Each form line is one small, tested step. You can follow any figure back to the form line it came from.

Supported today: Canada (federal), Ontario and Alberta, tax years 2025 and 2026 (2026 is provisional). More forms, lines, years and jurisdictions are added over time (see [Coverage](#coverage)).

## Example: a $70,000 salary (tax year 2025)

Given only a gross salary, the engine works out the contributions and tax from the CRA forms. Take-home is then salary minus CPP, EI and total tax, a subtraction done by the caller outside the engine:

| Item | Amount |
| --- | ---: |
| Federal tax | 7,585.64 |
| Ontario tax (ON428, incl. health premium) | 3,911.45 |
| **Total tax** | **11,497.09** |
| CPP contributions (base 3,291.75 + enhanced 665.00) | 3,956.75 |
| EI premiums | 1,077.48 |
| **Take-home** | **53,468.68** |

Every figure the engine computes comes with a trace saying how it was reached. Each trace line is about one figure (`line.label`), and its sentence names the figures it uses as the form prints them, so a caller shows the figure beside the sentence. This is the trace for the last Ontario line (ON428 line 90, "Ontario tax"):

```text
line 90: Line 88 (CA$3311.45) plus line 89 (CA$600.00) gives CA$3911.45 (rounded to the nearest cent).
```

## Why tax-engine

- **Explains itself.** A trace for every line: inputs, operation, result, rounding. A renderer turns it into text in any language; English is built today.
- **Mirrors the forms.** One form line is one capability, so engine steps read like the form itself.
- **Rules are data.** Rates, thresholds and limits are datasets copied as printed, never recomputed in code.
- **Follows the published forms.** The engine follows the CRA's published forms and formulas, including the T4127 payroll guide, line by line. It is an independent estimation tool and has not been reviewed or approved by the CRA.
- **Exact arithmetic.** `Decimal` everywhere, rounding only where the form says to round.
- **Jurisdiction-agnostic core.** Jurisdictions are plugins that add forms, datasets and capabilities; adding one does not change the core.

## Quick start

Requires Python 3.12 or newer. Install from [PyPI](https://pypi.org/project/tax-engine/):

```sh
pip install tax-engine
```

To work on the engine itself, install from a checkout instead:

```sh
git clone https://github.com/The-Pied-Piper/tax-engine.git
cd tax-engine
pip install -e .
```

Run the example, which prints the English trace for every form (the argument is the gross salary):

```sh
python examples/quickstart.py 70000
```

`examples/quickstart.py`:

```python
import sys
from decimal import Decimal

from tax_engine import build_tax_computation
from tax_engine.adapters.inbound.trace_english import EnglishNames, EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME

engine = build_tax_computation()
sheets = engine.compute(
    JurisdictionCode("CA-ON"), 2025, Artifact(EMPLOYMENT_INCOME, Decimal(sys.argv[1]))
)
for form, form_sheets in sheets.items():
    for sheet in form_sheets:
        print(f"\n== {form} ==")
        renderer = EnglishTraceRenderer()
        names = EnglishNames(sheet)
        for line in sheet.trace:
            # The sentence names the figures it uses as the form prints them when it is given
            # the worksheet; the figure the line is about is named beside it.
            sentence = renderer.render(line, sheet)
            print(sentence if line.label is None else f"{names.of_label(line.label)}: {sentence}")
```

The example uses Ontario (`CA-ON`) and tax year 2025. Change `CA-ON` to `CA-AB` for Alberta, and `2025` to `2026` for the provisional 2026 year.

## How it works

A jurisdiction's manifest lists the forms that make up a return. Each form is built line by line from small capabilities (sum, bracket tax, credit, cap, and so on) fed by parameter datasets for the tax year. The engine wires the forms together, runs them, and records a trace for every step.

## Coverage

| Jurisdiction | Year | Forms and lines built |
| --- | --- | --- |
| Canada (federal) | 2025, 2026 (provisional) | T1 General tax lines, Schedule 8 (CPP), T2204 (EI), Schedule 6 (Canada workers benefit), taxable income |
| Ontario | 2025, 2026 (provisional) | ON428 (Ontario tax), ON428-A (LIFT credit) |
| Alberta | 2025, 2026 (provisional) | AB428 (Alberta tax), Worksheet AB428 (Alberta supplemental tax credit) |

Roadmap: more forms and lines, and other provinces and territories. Forms are added one at a time, each built line by line from the CRA's own text.

## Disclaimer and limits

tax-engine is not tax advice and is not an official CRA product. It comes with no warranty, as the Apache-2.0 license says.

It covers tax years 2025 and 2026 (2026 is provisional), Canada (federal), Ontario and Alberta only, and only the forms and lines listed under Coverage. A return with items the engine does not model will not come out right. The take-home example assumes a single filer with salary as the only income.

Check any result against the CRA's own forms or with a professional before relying on it.

## Contributing

Issues and pull requests are welcome. Developer setup and checks are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
