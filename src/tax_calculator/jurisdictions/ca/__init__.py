"""Federal Canada (`CA`): the federal artifact catalog, the `ca/...` parameter datasets, its
capabilities and its trace lines.

Importing the package imports its `capabilities` package, which registers the federal capabilities,
its `trace` package of federal trace lines, and its `trace_english` package, which registers their
English renderers.
"""

NAMESPACE = "ca"

from tax_calculator.jurisdictions.ca import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
