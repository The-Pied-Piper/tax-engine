"""Alberta (`CA-AB`): its artifact catalog, the `ca-ab/...` datasets, its capabilities and its
trace lines.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-ab"

from tax_engine.jurisdictions.ca_ab import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
