__version__ = "0.1.0"

__all__ = (
    )

from ._machinery import bob, init_assistant

bob.initialize = init_assistant

bob.__version__ = __version__
