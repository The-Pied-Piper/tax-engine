# Manifest format

A jurisdiction manifest is YAML that selects capabilities and binds their slots to artifact
identifiers. `YamlJurisdictionSource`
(`src/tax_engine/adapters/outbound/yaml_jurisdictions.py`) reads it. Which slots a capability has,
and whether a slot takes one identifier or a list, are declared in code and checked when a
capability is built, not by the loader.

Parsing is strict: unknown keys, duplicate keys and wrongly typed values are rejected with the
offending file (for a folder, the offending part) named, and nothing is coerced or ignored.

## Where manifests live

The source takes a mapping of namespace to jurisdiction package directory. A jurisdiction's
namespace is its code lower-cased (`EX-ON` gives `ex-on`). Under `<package>/manifests/`:

- each `*.yaml` or `*.yml` file directly in the directory is one whole manifest;
- each subfolder holding such files is one manifest, merged from its parts: every `*.yaml` or
  `*.yml` file inside it, recursively, read in sorted path order.

A manifest whose `jurisdiction` is not the package's jurisdiction is rejected.

## Which manifest applies

A package may hold several manifests. For a tax year, `Jurisdiction.manifest_for` takes the one with
the greatest `valid_from_tax_year` that is not after the year. It raises `NotFoundError` if every
manifest starts later, and `AmbiguousManifestError` if two start in that greatest year. `version`
numbers the manifests and names them in that error.

## Example

A whole-file manifest with one input and one capability, under `ex-on/manifests/v1.yaml`:

```yaml
jurisdiction: EX-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: ex-on/levy_base
    required: true
outputs:
  - ex-on/levy
capabilities:
  - name: core/progressive_tax
    params:
      schedule: ex-on/brackets
    consumes:
      base: ex-on/levy_base
    produces:
      output: ex-on/levy
```

`ex-on/brackets` is a parameter family, read from `parameters/brackets/<tax year>.yaml` (see
[Parameter files](parameter-files.md)).

## Manifest keys

| Key | Required | Meaning |
| --- | --- | --- |
| `jurisdiction` | yes | The jurisdiction code, such as `EX-ON`. |
| `version` | yes | Integer. |
| `valid_from_tax_year` | yes | Integer. |
| `inputs` | yes | Non-empty list of input declarations (below). |
| `outputs` | yes | Non-empty list of artifact identifiers, none repeated: the exports of the default form. |
| `capabilities` | yes | List of capability selections (below). |
| `title` | no | Printed name of the default form. |
| `imports` | no | List of forms to import, each a form identifier `<namespace>/<snake_case>` or a form with dataset rebinds (see Imported forms). |

An identifier that is in both `inputs` and `outputs` is an input carried onto the return as entered.

## Forms

A manifest is a flat set of forms, peers that together are the return. The selections in the
top-level `capabilities` belong to the default form, named `<namespace>/return` (for example
`ex-on/return`), a required form whose exports are `outputs`. Two `outputs` with the same local id
(`ex/x` and `ca/x`, both `<namespace>/return.x`) are rejected.

Further forms of the manifest's own are declared only in a folder manifest, by parts with a
`form:` key (forms named by `imports` may be listed in a whole file too). A part with a `form:` key
gives all of its `capabilities` to that form. A single manifest file is not a part and takes no `form:` key.

The `form:` block has these keys:

| Key | Meaning |
| --- | --- |
| `name` | The form's identifier `<namespace>/<snake_case>`. Required in every part. The default form's name is reserved for parts without `form:`. |
| `exports` | The identifiers the form exports, `<namespace>/<snake_case>`, none repeated. |
| `instances` | The record-list artifact the caller supplies, one record per instance. Without it the form has one instance. Declared only together with `exports`. |
| `required` | `true` or `false`; required whenever `exports` is declared. |
| `required_when` | For an optional form, the yes/no artifact that says when the form is needed: a required input or an artifact a selection produces, never one of its own exports. A required form has none. |
| `basis` | For an optional form, the printed "Complete this form if" sentence. |
| `fields` | With `instances`, one declaration per field of the records, written like an input. A form without `instances` has none. |
| `max_instances` | Integer of at least 1: the most instances the form may have. |
| `min_instances` | Integer of at least 0, not above `max_instances`: the fewest. |
| `exclusive_group` | Identifier shared by forms of which at most one may have instances. |
| `title` | The form's printed name, such as `Schedule 8`. |
| `supplies` | Mapping from a neutral identifier to one of the form's own exports (see Supplied figures). |

A form may span several parts that carry the same `form.name`, in part order. Exactly one of them
declares `exports`, together with every other key of the block except `name`; a second part that
declares `exports`, or any of the other keys without `exports`, is rejected. A part with a `form:`
key takes no `outputs` or `imports`: exports are declared in the block. It may carry `inputs`, which
join the manifest's inputs like any part's, so a form carries the optional inputs it needs.

The limits apply to the count of instances; a form without `instances` has a default list of one
instance. Which fields the instances kind has, that defaults suit their kinds, and that
`required_when` is a yes/no count are checked when the manifest is loaded, against the artifact
kinds the source was given; an artifact those kinds do not have is an `InvalidManifestError`
naming the file.

## Supplied figures

A form that declares `exports` may also declare `supplies`, a mapping from a neutral identifier
`<namespace>/<snake_case>.<label>` (the form named by it need not exist) to one of its own exports,
which must be an amount, a count or a record list. The engine derives that kind as it does a form's
export, so every form reads it like `<form>.<export>`. One form supplies a given identifier; a
second is rejected, naming its part. `supplies` is allowed only in the part that declares `exports`.

## Imported forms

`imports` lists forms whose parts live in another package, so that several manifests share one
form. It may be in a whole file or in any part (lists from parts are concatenated in part order),
and no identifier is listed twice.

- The parts of an imported form are the `*.yaml` or `*.yml` files, recursively and sorted, in
  `<package of the namespace>/forms/<local id>/`, not under `manifests/`.
- They load with the manifest's own parts and take its jurisdiction, version and tax year, so each
  carries `form`, `capabilities` and `inputs`. Its `form.name` is the imported
  identifier, and exactly one part declares `exports`, as for any form.
- The `inputs` of an imported form's parts join the importing manifest's inputs, such as an
  optional input a salary-only caller leaves blank. An input declared there and also by the
  manifest, or by another imported form, is rejected, naming it and the part that listed it first.
- A part of the manifest that names an imported form, an import with no package or no parts, and an
  imported part with any other key are rejected, naming the part.
- An entry may instead be a mapping, to read other dataset families than the form's own:

  ```yaml
  imports:
    - ca/t1_taxable_income
    - form: ca/schedule_6
      datasets:
        ca/cwb_base_amount: ca-ab/cwb_base_amount
  ```

  `datasets` is a non-empty mapping from a family the form's selections read in `params` to the
  family to read instead, in this manifest alone; the form's files stay shared. Artifacts keep
  their names, even when one has the name of a family. Each family is named as the form's own
  files name it and is replaced once, so `a: b` with `b: c` reads `b` for `a` and `c` for `b`,
  never `c` for `a`. A family no part of the form reads is
  rejected. A target with no dataset, or of another kind than the slot takes, is rejected when the
  return is composed, as for any selection. An entry with no `datasets` is the bare identifier.
- The forms run in this order: the default form, the imported forms in `imports` order, then the
  manifest's own.
- An imported form that reads a derived figure (a `<form>.<export>` or a supplied identifier) that
  no form of the manifest derives is rejected, naming the form and the figure. Each importing
  manifest supplies such a figure from its own forms with `supplies`.

## Merging parts

In a folder manifest each part may carry any of the manifest keys, `title` and `form`.

- The scalar keys (`jurisdiction`, `version`, `valid_from_tax_year` and `title`, if given) must be
  in exactly one part. `title` is the default form's title, so it is not allowed in a part with a
  `form:` key.
- The lists (`inputs`, `outputs`, `capabilities`) are concatenated in part order. An identifier
  listed in two parts of `inputs`, or of `outputs`, is rejected.
- A part without `form:` joins the default form.

The merged mapping then goes through the same parse as a whole file.

## Input declarations

Each entry of `inputs` (and of a form's `fields`) is a mapping:

| Key | Meaning |
| --- | --- |
| `name` | The artifact identifier. Required. |
| `required` | `true` or `false`; always written, a bare identifier is rejected. |
| `default` | Optional input only. The value the request is read as when it leaves the line out: `null` for blank, a quoted figure such as `"0"`, `[]` or `""`. Present even when `null`. |
| `basis` | Optional input only. The printed sentence of the form that justifies the default. The loader keeps it and does not check it. |
| `title` | The figure's printed title. Optional, for either kind. |
| `reference` | What the form prints beside the figure, such as `10400` or `Box 14`. Optional, for either kind. |
| `unit` | The name of the figure's unit, such as `months`; see Units. Optional, for either kind. |

A required input takes neither `default` nor `basis`. By convention an entry writes `name`, `title`,
`reference` and `unit` first, then `required`, `default` and `basis`.

## Capability selections

Each entry of `capabilities` is a mapping:

| Key | Meaning |
| --- | --- |
| `name` | The capability's identifier. Required. |
| `produces` | Slot to artifact identifier. Required, at least one slot. |
| `params` | Slot to parameter family. Optional. |
| `consumes` | Slot to an artifact identifier, or to a list of identifiers kept in order. Optional. |
| `blank` | What a blank does (below). Optional; a consumed slot not named refuses a blank. |
| `title` | The printed wording of the one figure the selection produces. A selection that produces several figures is rejected if it has one. |
| `reference` | What the form prints beside that figure, as free text. Same one-figure rule. |
| `unit` | The name of that figure's unit; see Units. Same one-figure rule. |

A selection writes `name`, `title`, `reference` and `unit` before its other keys.

### Blank rules

Under `blank`, a name is a consumed slot, or one artifact identifier in a list slot. Its value is
one of:

- `pass_on`: a blank there blanks everything the selection produces;
- `compute`: the capability's code decides;
- the text of a fallback number, read as the value type of the kinds the slot (or the one artifact)
  takes, and taken in the blank's place.

A name may instead map to a mapping of record field identifier to rule, for a consumed record-list
slot: the rule then applies to that field in every record.

## Titles

`title` and `reference` are for the reader of a trace. All are non-empty text, optional, and never
used to look anything up: the identifier stays the unique name.

## Units

`unit` on an input, a field or a selection names the unit of one figure: the words or symbol its
number is written with in a trace, `EX$3500.00` or `12 months`. A unit is bare snake_case, never
`<namespace>/<name>`, and a figure with none prints as it always has. The `name` is the
language-neutral key; a unit's text (`EX$`, `moons`) is English wording, which another language's
renderer replaces.

A package declares units on a `UnitCatalog` in its `units.py` (see
[Jurisdiction packages](jurisdiction-packages.md)). A manifest of jurisdiction `EX-ON` finds a name
among the units of core, of `ex-on` and of its country `ex`: a province uses its federal package's
units, never another province's. A name found nowhere is an `InvalidManifestError` naming the file
and the declaration when the manifest is loaded, and a name found in more than one of those
packages is refused as ambiguous.

A unit is carried as data with the figure, as `Artifact.unit` and `Worksheet.unit`, so a reader of
the results needs no English. A figure is read in one unit by every form that reads it and every
form that produces it: forms that disagree, including one that names a unit and one that names
none, are an `InvalidCompositionError` naming the figure and the forms. A figure that two
declarations of a manifest name must therefore name the same unit in both. A figure a form imports
from another form takes the unit of the exporting form, which is what the importing form prints
and `Worksheet.unit` reads. The manifest alone decides a figure's unit: an artifact a caller hands
in with a unit of its own is stamped with the manifest's, or with none. Real manifests and
datasets name no unit.
