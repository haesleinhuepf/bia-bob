from IPython.core.getipython import get_ipython
from IPython.core.magic import register_line_cell_magic
from IPython.display import display

from ._utilities import generate_response, output_text


class Context:
    assistant = None
    variables = None
    verbose = False


# @register_line_cell_magic
# def xbob(line: str = None, cell: str = None):
#     """Sends a prompt to openAI
#     and shows the text and code response
#     and executes the code!
#     """
#
#     # update the context, note that globals() does not work
#     Context.variables = get_ipython().user_ns
#     user_input = combine_user_input(cell, line)
#
#     if user_input is None:
#         display("Please ask a question!")
#
#     result = Context.assistant.generate_and_execute_response(input=user_input)
#     output_text(result)


@register_line_cell_magic
def ai(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and pastes the code into the next cell.
    """

    if Context.assistant is None:
        display("Please first init the assistant!")
        return

    user_input = combine_user_input(cell, line)
    if user_input is None:
        display("Please ask a question!")
        return

    Context.variables = get_ipython().user_ns
    Context.assistant.generate_response(user_input=user_input)

# @register_line_cell_magic
# def bob(line: str = None, cell: str = None):
#     """Sends a prompt to openAI
#         and shows the text and code response
#         but does NOT execute the code!
#         """
#     Context.variables = get_ipython().user_ns
#     user_input = combine_user_input(cell, line)
#
#     if user_input is None:
#         display("Please ask a question!")
#
#     result = Context.assistant.generate_response(user_input)
#
#     output_text(result)


def combine_user_input(cell, line):
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
    def __init__(self, model="gpt-3.5-turbo", temperature=0):
        self.model = model
        self.temperature = temperature

    # def generate_response(self, input: str):
    #     """Sends a prompt to openAI
    #     and shows the text and code response.
    #     """
    #     code, text = generate_response(input, self.model)
    #     output_text(text)
    #     output_code(code)
    #
    #     return "Response was generated."

    # def generate_and_execute_response(self, input: str):
    #     """Sends a prompt to openAI
    #     and shows the text and code response
    #     and immediately executes the code.
    #     """
    #     code, text = generate_response(input)
    #     output_text(text)
    #     output_code(code)
    #
    #     exec(code, Context.variables)
    #
    #     if Context.verbose:
    #         print("Execution done.")
    #
    #     return "Code was generated and executed."

    def generate_response(self, user_input: str):
        """Sends a prompt to openAI
        and shows the text and code response
        and pastes the code into the next cell.
        """
        code, text = generate_response(user_input, self.model)

        text = text + "\n#### Additional information\n\n"
        if code is None:
            text = text + "The response did not contain any code."
        else:
            text = text + ("The code was put into the next cell.  It is your responsibility to carefully check it "
                           "before executing it!")

        output_text(text)
        output_code(code)


def init_assistant(model="gpt-3.5-turbo", temperature=0):
    Context.assistant = CustomAgent(model, temperature)
    print("Assistant initialised.\n\nYou can call it using the %ai command, e.g.\n\n%ai please generate a random 2D "
          "grayscale image.")
