"""Federal Canada (`CA`): the federal artifact catalog, the `ca/...` parameter datasets, its
capabilities and its trace lines.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca"

from tax_engine.jurisdictions.ca import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
