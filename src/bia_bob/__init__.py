__version__ = "0.25.1"

__all__ = (
)

from ._machinery import bob, init_assistant, enable_plugins
from ._accelerate import acc
from ._bug_fixing import fix
from ._document import doc
from ._utilities import available_models
from ._notebook_generation import generate_notebook
from ._utilities import ask_llm

bob.initialize = init_assistant
bob.__version__ = __version__
bob.enable_plugins = enable_plugins
