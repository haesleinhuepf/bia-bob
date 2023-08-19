__version__ = "0.2.3"

__all__ = (
    )

from ._machinery import bob, init_assistant, add_function_tool
from ._speech_recognition import _listen
from ._speak import _speak, _quiet
bob.initialize = init_assistant
bob.add_function_tool = add_function_tool

bob.__version__ = __version__
bob.listen = _listen
bob.speak = _speak
bob.quiet = _quiet
