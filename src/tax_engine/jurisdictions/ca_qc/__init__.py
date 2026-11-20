"""Quebec (`CA-QC`): its artifact catalog, its capabilities, its trace lines and
its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-qc"

from tax_engine.jurisdictions.ca_qc import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
