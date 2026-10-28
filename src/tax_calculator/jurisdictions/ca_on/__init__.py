"""Ontario (`CA-ON`): its artifact catalog, the CA-ON manifest and the `ca-on/...` datasets.

The manifest also selects federal capabilities, whose kinds and data live in `tax_calculator.jurisdictions.ca`.
Importing the package imports its `capabilities` package, which registers Ontario's capabilities,
its `trace` package of Ontario trace lines, and its `trace_english` package, which registers their
English renderers.
"""

NAMESPACE = "ca-on"

from tax_calculator.jurisdictions.ca_on import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
