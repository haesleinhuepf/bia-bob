__version__ = "0.1.0"

__all__ = (
    )

from ._machinery import tischi, init_assistant, add_function_tool

tischi.initialize = init_assistant
tischi.add_function_tool = add_function_tool

tischi.__version__ = __version__
