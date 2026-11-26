"""Nova Scotia (`CA-NS`): its artifact catalog, its capabilities, its trace lines and
its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-ns"

from tax_engine.jurisdictions.ca_ns import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
