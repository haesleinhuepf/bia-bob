__version__ = "0.2.0"

__all__ = (
    )

from ._machinery import bob, init_assistant, add_function_tool
bob.initialize = init_assistant
bob.add_function_tool = add_function_tool

bob.__version__ = __version__
