"""Core: the mechanisms every jurisdiction may use, identified under `core/`.

A package like any jurisdiction's, with an empty artifact catalog and no data folders; its
`capabilities` and `parameter_parsers` packages hold the generic mechanisms and its `units` module
declares the generic units.

Importing the package imports its `trace_english` package.
"""

NAMESPACE = "core"

from tax_engine.jurisdictions.core import trace_english  # noqa: E402

__all__ = ["NAMESPACE", "trace_english"]
