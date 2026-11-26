"""Prince Edward Island (`CA-PE`): its artifact catalog, the `ca-pe/...` datasets, its capabilities,
its trace lines and its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-pe"

from tax_engine.jurisdictions.ca_pe import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
