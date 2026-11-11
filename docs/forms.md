# Forms

A computation is a flat set of forms that together are the return; none is special. A form is a
group of capabilities with the artifacts it exports, never a capability itself. The code is in
`tax_engine.domain.form` (wiring and running) and `tax_engine.domain.manifest` (declaration).

## Wiring one form

`FormComposition` wires one form as an inner `Composition` whose outputs are the form's exports and
whose inputs are derived. The inputs are:

- the starting artifacts the form reads;
- the fields of its `instances` kind (a record-list kind, one record per instance), if it has one;
- its imports, the kinds it reads that other forms export.

A form without an `instances` list has exactly one implicit instance.

For each export `X` of form `B`, the engine derives the kind `B.X`: a record list of one field,
`X`, with a record per instance in instance order (one record for a form without an instances
list). Every form reads such a kind by its identifier; an export nobody reads is allowed. A form
that reads its own `B.X` gets, in each run, the record list of that export over the runs before
it, in run order (empty in the first). Only amount, count and record-list exports are derived.

## Running the forms

`FormSet` holds the forms of one computation. It orders them by their imports, runs each once per
instance record on its own `Worksheet`, keeps every form's exports in one store, hands each run its
imports as starting artifacts, and returns a mapping from form name to one `Worksheet` per
instance, in instance order.

## Required and optional forms

`required` says whether the return must include the form. An optional form names the yes/no
artifact that says when it is needed in `required_when`, the machine form of its printed "Complete
this form if ..." sentence (kept as `basis`); a required form has neither, and an optional form may
not be gated by one of its own exports. A form with an instances list declares each field of its
records in `fields`; a form without one has no fields. A field of a required form, or of an
attached optional form, is required only when the form is attached.

## Instance limits

A form without an instances list has a default list of exactly one instance, and the limits apply
to the length of its list uniformly.

- `max_instances` is the most records the caller may give (an integer of at least 1).
- `min_instances` is the fewest (an integer of at least 0, not above the maximum).
- An `exclusive_group` is shared by forms of which at most one may have instances. With none, the
  group exports nothing, so a total of its forms' exports is zero.

`FormSet` refuses a caller who breaks a limit with a `ValidationError` naming the form or the group.
It refuses at construction a group that names only one form, or in which two forms always have
instances (each could never hold).

## Supplied figures

A form's `supplies` maps a neutral identifier `<namespace>/<snake_case>.<label>` to one of its own
exports. The identifier is spelt like a form export's but names a form that need not exist: the
engine derives it as the record list of that export's one field, so every form reads it as it reads
`<form>.<export>`. A manifest uses it so that a form it imports reads a figure under a name no
jurisdiction is part of, and each jurisdiction supplies it from its own forms. Only an export a
record can hold (an amount, a count or a record list) may be supplied, and one identifier is
supplied by one form only; a clash with a derived `<form>.<export>` is an `InvalidManifestError`.
