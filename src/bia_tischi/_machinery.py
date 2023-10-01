from IPython.core.getipython import get_ipython
from IPython.core.magic import register_line_cell_magic
from IPython.display import display

from ._utilities import generate_response, output_text


class Context:
    assistant = None
    variables = None
    verbose = False


class Models:
    models = ["gpt-3.5-turbo", "gpt-4.0"]
    input_price = [0.0015, 0.03]
    output_price = [0.002, 0.06]

    @classmethod
    def supported_models(cls):
        return cls.models

    @classmethod
    def input_price_per_1k_token(cls, model: str) -> float:
        index = cls.models.index(model)
        return cls.input_price[index]

    @classmethod
    def output_price_per_1k_token(cls, model: str) -> float:
        index = cls.models.index(model)
        return cls.output_price[index]


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

    # set context variables
    Context.variables = get_ipython().user_ns

    # generate the response
    Context.assistant.generate_response(user_input)


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
        user_input = None
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
        and shows the text response
        and pastes the code into the next cell.
        """
        code, text = generate_response(user_input, self.model)

        if code is None:
            text = text + "The response did not contain any code."
        else:
            text = text + ("The code was put into the next cell.\n\n"
                           "It is **your responsibility to carefully check it** before executing!\n\n")

        output_text(text)

        if code is not None:
            get_ipython().set_next_input(code, replace=False)


def init_assistant(model="gpt-3.5-turbo", temperature=0):
    Context.assistant = CustomAgent(model, temperature)
    print("Assistant initialised.\n\nYou can call it using the %ai command, e.g.\n\n%ai please generate a random 2D "
          "grayscale image.")
