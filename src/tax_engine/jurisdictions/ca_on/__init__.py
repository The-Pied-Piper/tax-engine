"""Ontario (`CA-ON`): its artifact catalog, the `ca-on/...` datasets, its capabilities and its
trace lines.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-on"

from tax_engine.jurisdictions.ca_on import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
