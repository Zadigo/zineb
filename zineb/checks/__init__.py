# Preload these modules so that the checks
# registry is populated via the registry decorator
from zineb.checks import base, http, server

__all__ = ['base', 'http', 'server']
