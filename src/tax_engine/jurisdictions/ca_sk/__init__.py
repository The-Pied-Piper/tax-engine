"""Saskatchewan (`CA-SK`): its artifact catalog, the `ca-sk/...` datasets, its capabilities, its
trace lines and its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-sk"

from tax_engine.jurisdictions.ca_sk import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
