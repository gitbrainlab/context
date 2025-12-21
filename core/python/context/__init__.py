"""
Context: A lightweight, cross-runtime execution abstraction for LLM requests.

The Context abstraction shapes how LLM requests are executed across backend
automation and frontend browser environments.
"""

from .context import Context
from .executor import Executor
from .pruner import Pruner
from .router import Router

__version__ = "0.1.0"
__all__ = ["Context", "Executor", "Pruner", "Router"]
