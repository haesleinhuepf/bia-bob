__version__ = "0.11.0"

__all__ = (
)

from ._machinery import bob, init_assistant, enable_plugins
from ._bug_fixing import fix
from ._document import doc
from ._utilities import available_models

bob.initialize = init_assistant
bob.__version__ = __version__
bob.enable_plugins = enable_plugins
