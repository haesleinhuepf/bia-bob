from IPython.core.getipython import get_ipython
from IPython.core.magic import register_line_cell_magic
from IPython.display import display

from ._utilities import generate_response_to_user, output_text


class Context:
    assistant = None
    variables = None
    verbose = False
    chat = []


@register_line_cell_magic
def ai(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and pastes the code into the next cell.
    """

    if Context.assistant is None:
        init_assistant()

    user_input = combine_user_input(line, cell)
    if user_input is None:
        display("Please ask a question!")
        return

    # set context variables
    Context.variables = get_ipython().user_ns

    # generate the response
    Context.assistant.generate_response_to_user(user_input)


def combine_user_input(line, cell):
    if line and cell:
        user_input = line + "\n" + cell
    elif line:
        user_input = line
    elif cell:
        user_input = cell
    else:
        user_input = None
    return user_input


class CustomAgent:
    def __init__(self, model="gpt-3.5-turbo", temperature=0):
        self.model = model
        self.temperature = temperature

    def generate_response_to_user(self, user_input: str):
        """Sends a prompt to openAI
        and shows the text response
        and pastes the code into the next cell.
        """
        code, text = generate_response_to_user(self.model, user_input)

        output_text(text)

        if code is not None:
            get_ipython().set_next_input(code, replace=False)


def init_assistant(model="gpt-3.5-turbo", temperature=0):
    Context.assistant = CustomAgent(model, temperature)
    if Context.verbose:
        print("Assistant initialised. You can now use it, e.g., copy and paste the"
          "below two lines into the next cell and execute it."
          "\n\n%%ai"
          "\nplease generate a noisy grayscale image containing 10 blurry blobs with a diameter of 20 pixels each.")
