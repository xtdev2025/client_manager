"""Deprecated module retained for backward compatibility.

All public template routes were removed to simplify the application surface. This
module intentionally raises an error if imported so that any lingering imports
fail fast and prompt cleanup.
"""

raise RuntimeError(
	"app.controllers.public_template was removed. Remove any references to the "
	"public template blueprint."
)
