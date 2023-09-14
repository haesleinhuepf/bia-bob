__version__ = "0.1.0"

__all__ = (
    )

from ._machinery import tischi, init_assistant

tischi.initialize = init_assistant

tischi.__version__ = __version__
