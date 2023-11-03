__version__ = "0.4.0"

__all__ = (
)

from ._machinery import bob, init_assistant
from ._bug_fixing import fix
from ._document import doc

bob.initialize = init_assistant
bob.__version__ = __version__


from ._fine_tuning import FineTuningFromQuestionsAndAnswers
