# Parameter files

A parameter dataset is a YAML file holding one family's values of one kind for one tax year.
`YamlParameterSource` (`src/tax_engine/adapters/outbound/yaml_parameters.py`) reads it. The value
objects the kinds produce are described in [Parameter data](parameter-data.md).

## Where a file lives

The family `ex-on/brackets` for tax year 2025 is
`<package of the ex-on namespace>/parameters/brackets/2025.yaml`. The first segment of the family is
its namespace and the rest, which may nest, is its path under `parameters/`. A year with no file is
`NotFoundError`; a year is never carried forward from an earlier one.

## Envelope

Every file has the same envelope, plus keys specific to its kind, which that kind's parser reads.

| Key | Required | Meaning |
| --- | --- | --- |
| `family` | yes | The family asked for, such as `ex-on/brackets`. |
| `tax_year` | yes | The tax year asked for, an integer. |
| `kind` | yes | The parameter kind asked for, such as `brackets`. |
| `sources` | yes | A non-empty list of strings naming where the figures come from. |
| `rounding` | yes | `none`, or a mapping of `increment` (a quoted positive decimal) and `mode` (such as `half_up`). |
| `title` | no | The wording the form prints for the figure, such as `maximum per slip`. Non-empty text. |

The file must declare the family, year and kind that were asked for, or it is rejected. Unknown,
missing and duplicate keys and wrongly typed values are rejected, and every error names the file.

Decimals and whole-number figures in a kind's own keys are quoted YAML strings (`"0.145"`, `"3"`),
so they never pass through a float and each number has one spelling.
