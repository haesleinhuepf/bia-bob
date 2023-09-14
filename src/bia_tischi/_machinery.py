class _context():
    variables = None
    verbose = False


from IPython.core.magic import register_line_cell_magic


@register_line_cell_magic
def tischi(line: str = None, cell: str = None):
    from IPython.display import display, Markdown
    if _context.agent is None:
        init_assistant({})

    if _context.verbose:
        print("Variables:", len(_context.variables.keys()))

    if line and cell:
        prompt = line + "\n" + cell
    elif line:
        prompt = line
    elif cell:
        prompt = cell
    else:
        display("Please enter a question behind %tischi")
        return ""

    result = _context.agent.run(input=prompt)

    display(Markdown(result))

class CustomAgent:
    def __init__(self):
        pass

    def run(self, input: str):
        """A prompt helper function that sends a message to openAI
        and returns only the text response.
        """
        from ._utilities import generate_and_execute_code
        generate_and_execute_code(input)
        return ""


def init_assistant(variables, temperature=0):
    if _context.verbose:
        print("Initializing assistant")

    _context.agent = CustomAgent()

    # store the variables
    _context.variables = variables



init_assistant(globals())
