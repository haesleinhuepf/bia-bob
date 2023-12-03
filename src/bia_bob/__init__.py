__version__ = "0.6.0"

__all__ = (
)

from ._machinery import bob, init_assistant, set_seed
from ._bug_fixing import fix
from ._document import doc
from ._utilities import available_models

bob.initialize = init_assistant
bob.set_seed = set_seed
bob.__version__ = __version__
