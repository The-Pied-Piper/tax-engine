"""Parsers for the kind-specific part of the generic YAML parameter datasets.

Each parser handles one parameter kind: the keys it adds to a dataset file and how to turn them
into that kind's values. Nothing lists them: the composition root builds a
`ParameterParserRegistry` by walking this package's modules (`tax_engine.registrations`), so a
new parser is a new module here.
"""
