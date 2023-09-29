
from IPython.core.magic import register_line_cell_magic
from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown, Javascript
from ._utilities import generate_response, output_text, output_code

class _context():
    agent = None
    variables = None
    verbose = False

@register_line_cell_magic
def vars(line):
    globals = get_ipython().user_ns
    print("Globals:", globals.keys())
    for name, value in globals.items():
        if not name.startswith('_') and not callable(value):
            print(name)


@register_line_cell_magic
def populate_next_cell(line):
    # Define the code to be inserted into the next cell
    code = """
# This is some custom code
def hello_world():
    print("Hello, World!")
    """

    get_ipython().set_next_input(code, replace=False)

@register_line_cell_magic
def xbob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and executes the code!
    """

    # update the context, note that globals() does not work
    _context.variables = get_ipython().user_ns
    user_input = init_agent_and_combine_user_input(cell, line)

    if user_input is None:
        display("Please ask a question!")

    result = _context.agent.generate_and_execute_response(input=user_input)
    output_text(result)


@register_line_cell_magic
def cbob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and pastes the code into the next cell.
    """

    # update the context, note that globals() does not work
    _context.variables = get_ipython().user_ns
    user_input = init_agent_and_combine_user_input(cell, line)

    if user_input is None:
        display("Please ask a question!")

    result = _context.agent.generate_response_and_paste_code_in_next_cell(input=user_input)
    output_text(result)


@register_line_cell_magic
def bob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
        and shows the text and code response
        but does NOT execute the code!
        """
    _context.variables = get_ipython().user_ns
    user_input = init_agent_and_combine_user_input(cell, line)

    if user_input is None:
        display("Please ask a question!")

    result = _context.agent.generate_response(user_input)

    output_text(result)


def init_agent_and_combine_user_input(cell, line):
    if _context.agent is None:
        print("Initializing new AI assistant.")
        init_agent(_context.variables)
    if _context.verbose:
        print("Variables:", _context.variables.keys())
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
        and shows the text and code response.
        """
        code, text = generate_response(input)
        output_text(text)
        output_code(code)

        return "Response was generated."

    def generate_and_execute_response(self, input: str):
        """Sends a prompt to openAI
        and shows the text and code response
        and immediately executes the code.
        """
        code, text = generate_response(input)
        output_text(text)
        output_code(code)

        exec(code, _context.variables)

        if _context.verbose:
            print("Execution done.")

        return "Code was generated and executed."


    def generate_response_and_paste_code_in_next_cell(self, input: str):
        """Sends a prompt to openAI
        and shows the text and code response
        and pastes the code into the next cell.
        """
        code, text = generate_response(input)

        output_text(text)
        get_ipython().set_next_input(code, replace=False)

        return ("Code was put into the next cell.\n"
                "Carefully check it before executing it!\n"
                "It is your responsibility to run it!")


def init_agent(variables, temperature=0):
    if _context.agent is not None:
        print("Agent and context have been initialized already.")
        return

    _context.agent = CustomAgent()

    # store the variables
    _context.variables = variables

    print("Agent and context initialised.")
