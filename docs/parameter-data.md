# Parameter data

Parameter values are data resolved per family and tax year; the code holds no jurisdiction's
tables, thresholds, rates or rounding. The value objects live in `tax_engine.domain.parameters`
and check themselves when built.

## Bracket schedules (`brackets.py`)

A bracket holds the threshold it starts from (`lower`), its `rate` and, optionally, the tax at its
start as the form prints it (`tax_at_start`).

- A printed `tax_at_start` is used as given, neither computed nor rounded.
- Without one, the tax at the start is the exact cumulative tax on the brackets below (never a sum
  of rounded figures), rounded with the schedule's `tax_at_start_rounding`. The first bracket's is 0,
  put through the same rule. The default rule is none, so the result is the exact sum.
- The tax on an amount is the form's two lines for the bracket the amount falls in: the rate on the
  excess over the bracket's lower, plus its tax at start. An amount at a threshold falls in the
  lower bracket ("more than ... but not more than ...").
- Rounding the column's tax is the capability's decision, made with its own rounding rule.
- A schedule covers a range of amounts. The first bracket's `from` is where it starts ("more than":
  0 itself is covered only when `from` is 0). The optional `up_to` is the last amount it covers
  ("not more than"); it must lie above the last bracket's `from`. Without `up_to` the schedule has
  no upper end. `covers(amount)` says whether an amount is in the range.
- A first bracket above 0 must print its `tax_at_start`, since the schedule cannot compute the tax
  below its range. A later bracket without a printed start then adds the exact tax on the brackets
  between to that printed figure, rounded with `tax_at_start_rounding`.
- A ranged schedule (an `up_to`, or a first bracket above 0) is how a form prints two tables side by
  side, each filled in only for the incomes it covers. `column_for` and `tax_on` refuse an amount
  outside the range (`AmountOutsideBracketRangeError`); the `bracket_column_*` capabilities instead
  give a blank, with a trace line saying the base is outside the range, which later steps pass on.
  A schedule from 0 with no `up_to` covers every amount from 0 and behaves as before.

## Amount by band (`amount_by_band.py`)

A band is one row of a chart: `over`, the lower bound the row starts above, and either a flat
`amount` or a sloped figure `(income - minus) x rate + plus`. A row is flat (`amount` alone) or
sloped (`minus`, `rate` and `plus` all set); any other mix is an error. Figures are exact, finite
and not negative. The dataset's rounding rule is applied by the capability.

## Rate tables (`rate_table.py`)

Each row is printed as "more than X but not more than Y: rate" (the last row has no upper bound).
The table also holds `rate_at_zero`, the rate for a figure of exactly zero. Bounds are exact and
kept as printed: an overlap between a row's upper bound and the next row's lower bound, as a form's
typo can print, is kept, while a gap is refused. A figure above zero falls in the last row whose
`more_than` it exceeds, so in an overlap the later row applies.

## Class rates (`class_rates.py`)

Each class is keyed by its number as printed, an exact `Decimal` so that a class such as 10.1 is a
number. It holds its `rate`, whether the half-year rule applies to it (and on sale,
`half_year_rule_on_sale`), whether recapture and a terminal loss apply to it, and two factors,
`aiip_factor` and `riip_factor`. The factors are `Fraction`s kept as given, so a printed factor of
0 is allowed. A class may list `elections`, each a whole `code` above 0 and the `rate` a row takes
when the caller elects that code. The table holds at least one class, no class number twice, in the
order given; a class it does not list is `None`. It also holds `full_year_days`, the positive
number of days in a full fiscal period, against which a first fiscal period of fewer days is
prorated, and `longest_fiscal_period_days`, the most days a fiscal period may have (a whole number
of at least `full_year_days`).

## Conditions (`conditions.py`)

A form line switched on or off by a list of conditions ("enter 0 if any of them applies") is copied
as printed.

- A `ConditionList` holds `count_when_any_applies` (0 or 1) and one or more `Condition`s. When no
  condition applies the count is the other of 0 and 1.
- A `Condition` holds its printed `text` and `parts`, all of which must hold.
- A `ConditionPart` holds `tests`, any one of which holds ("and" joins parts, "or" joins tests).
- A `ConditionTest` compares one figure with a printed figure (`than`) or another amount
  (`against`).
- Figures are named by position (from 1) in the capability's list of counts or of amounts, so a
  figure read by several tests is listed once.

## Rounding (`rounding.py`)

Rounding is a parameter, never a constant in code. A capability decides where it rounds, as does a
parameter value that computes a figure of its own (a bracket schedule's tax at each start); the
`RoundingRule` decides how. The default `NO_ROUNDING` leaves amounts exact, so every rounding point
calls `apply` and an unconfigured rule changes nothing.

Only exact amounts are accepted: a `Decimal`, or the exact `Fraction` a capability gets by dividing.
Rounding works on exact fractions, so any positive increment (0.01, 1, 0.05, ...) rounds without an
inexact division. The engine runs capabilities under a `decimal` context that traps `Inexact`;
`apply` is the one place allowed to be inexact. `NO_ROUNDING` never rounds, so a quotient with no
finite decimal expansion raises `decimal.Inexact`.

## Fractions (`fraction.py`)

A rate must be a finite decimal, and two-thirds is not, so a fraction is carried as its numerator
(zero or more) and its positive denominator, kept as given and never reduced. The capability that
applies it does the one division.
