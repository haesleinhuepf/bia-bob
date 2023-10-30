__version__ = "0.3.0"

__all__ = (
)

from ._machinery import bob, init_assistant
from ._bug_fixing import fix

bob.initialize = init_assistant
bob.__version__ = __version__
