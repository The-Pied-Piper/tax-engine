"""Manitoba (`CA-MB`): its artifact catalog, the `ca-mb/...` datasets, its capabilities, its trace
lines and its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-mb"

from tax_engine.jurisdictions.ca_mb import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
