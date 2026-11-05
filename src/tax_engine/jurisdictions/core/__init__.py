"""Core: the mechanisms every jurisdiction may use, identified under `core/`.

A package like any jurisdiction's, without data folders or an artifact catalog: its
`capabilities` package holds the generic capabilities and its `parameter_parsers` package the
parsers of the generic parameter kinds. Both are found by the composition root walking them
(`tax_engine.registrations`).
"""

NAMESPACE = "core"
