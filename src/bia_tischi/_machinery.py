
from IPython.core.magic import register_line_cell_magic
from IPython.display import display, Markdown
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
        code, full_response = generate_response(input)
        output_text(full_response)
        # output_code(code) # already part of the full response

        return "Response was generated."

    def generate_and_execute_response(self, input: str):
        """Sends a prompt to openAI
        and shows the text and code response
        and immeditately executes the code.
        """
        code, full_response = generate_response(input)
        output_text(full_response)
        output_code(code)

        exec(code, _context.variables)

        if _context.verbose:
            print("Execution done.")

        return "Code was generated and executed."



def init_agent(variables, temperature=0):
    if _context.agent is not None:
        print("Agent and context have been initialized already.")
        return

    _context.agent = CustomAgent()

    # store the variables
    _context.variables = variables

    print("Agent and context initialised.")
