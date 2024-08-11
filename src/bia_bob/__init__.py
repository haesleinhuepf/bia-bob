__version__ = "0.21.1"

__all__ = (
)

from ._machinery import bob, init_assistant, enable_plugins
from ._accelerate import acc
from ._bug_fixing import fix
from ._document import doc
from ._utilities import available_models
from ._notebook_generation import generate_notebook
from ._utilities import ask_llm, Context

bob.initialize = init_assistant
bob.__version__ = __version__
bob.enable_plugins = enable_plugins

def ask_llm(prompt, image=None, chat_history=[]):
    if Context.model is None:
        init_assistant()
    return ask_llm(prompt, image, chat_history)
