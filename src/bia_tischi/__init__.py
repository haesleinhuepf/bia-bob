__version__ = "0.1.0"

__all__ = (
)

from ._machinery import ai, init_assistant

ai.initialize = init_assistant
ai.__version__ = __version__
