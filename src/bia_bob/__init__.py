__version__ = "0.6.2"

__all__ = (
)

from ._machinery import bob, init_assistant
from ._bug_fixing import fix
from ._document import doc
from ._utilities import available_models

bob.initialize = init_assistant
bob.__version__ = __version__
