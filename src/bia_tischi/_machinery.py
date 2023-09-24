
from IPython.core.magic import register_line_cell_magic
from IPython.display import display, Markdown
from ._utilities import generate_response, display_in_notebook

class _context():
    variables = None
    verbose = False

@register_line_cell_magic
def xbob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and executes the code!
    """

    user_input = update_context_and_create_user_input(cell, line)

    if user_input is None:
        display("Please ask a question!")

    result = _context.agent.generate_and_execute_response(input=user_input)

    display_in_notebook(Markdown(result))

@register_line_cell_magic
def bob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
        and shows the text and code response
        but does NOT execute the code!
        """

    user_input = update_context_and_create_user_input(cell, line)

    if user_input is None:
        display("Please ask a question!")

    result = _context.agent.generate_response(user_input)

    display_in_notebook(Markdown(result))


def update_context_and_create_user_input(cell, line):
    if _context.agent is None:
        init_assistant({})
    if _context.verbose:
        print("Variables:", len(_context.variables.keys()))
    if line and cell:
        user_input = line + "\n" + cell
    elif line:
        user_input = line
    elif cell:
        user_input = cell
    else:
        user_input = none
    return user_input


class CustomAgent:
    def __init__(self):
        pass

    def generate_response(self, input: str):
        """Sends a prompt to openAI
        and shows  the text and code response.
        """
        code, full_response = generate_response(input)
        display_in_notebook(full_response)

        if _context.verbose:
            print("Execution:")

        exec(code, _context.variables)

        if _context.verbose:
            print("Execution done.")

        return "Response was generated."

    def generate_and_execute_response(self, input: str):
        """Sends a prompt to openAI
        and shows the text and code response
        and immeditately executes the code.
        """
        code, full_response = generate_response(input)
        display_in_notebook(full_response)

        if _context.verbose:
            print("Execution:")

        exec(code, _context.variables)

        if _context.verbose:
            print("Execution done.")

        return "Code was generated and executed."



def init_assistant(variables, temperature=0):
    if _context.verbose:
        print("Initializing assistant")

    _context.agent = CustomAgent()

    # store the variables
    _context.variables = variables



init_assistant(globals())
