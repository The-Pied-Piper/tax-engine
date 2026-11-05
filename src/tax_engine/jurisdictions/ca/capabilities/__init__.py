"""Federal Canada's capabilities: mechanisms specific to its forms, parameters from data.

Each capability is decorated with `@capability`, which gives it its identifier; nothing lists them:
the composition root builds a `CapabilityRegistry` by walking this package's modules
(`tax_engine.registrations.capabilities`). A new capability is a new module here.
`NAMESPACE` is the namespace of every identifier declared here.
"""

NAMESPACE = "ca"
