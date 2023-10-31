from IPython.core.getipython import get_ipython
from IPython.core.magic import register_line_cell_magic
from IPython.display import display

from ._utilities import generate_response_to_user, output_text, keep_available_packages


class Context:
    assistant = None
    variables = None
    verbose = False
    auto_execute = False
    chat = []
    libraries = keep_available_packages([
        "scikit-image",
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "stackview",
        "torch",
        "pytorch-lightning",
        "cellpose",
        "stardist",
        "n2v",
        "pyclesperanto-prototype",
        "apoc",
        "napari-segment-blobs-and-things-with-membranes",
        "napari-simpleitk-image-processing",
        "napari-skimage-regionprops",

        # to add libraries here, add their pypi package names (not their import names)
    ])


@register_line_cell_magic
def bob(line: str = None, cell: str = None):
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
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0):
        self.model = model
        self.temperature = temperature

    def generate_response_to_user(self, user_input: str):
        """Sends a prompt to openAI
        and shows the text response
        and pastes the code into the next cell.
        """
        code, text = generate_response_to_user(self.model, user_input, temperature=self.temperature)

        if code is None or not Context.auto_execute:
            output_text(text)

        if code is not None:
            p = get_ipython()
            if Context.auto_execute:
                p.set_next_input(code, replace=True)
                p.run_cell(code)
            else:
                p.set_next_input(code, replace=False)
            


def init_assistant(model: str = "gpt-3.5-turbo", temperature: float = 0, auto_execute: bool = False, variables: dict = None):
    """Initialises the assistant.

    Parameters
    ----------
    model: str
    temperature: float, optional (default: 0, between 0 and 1) The higher the temperature, the more random the output.
    auto_execute: bool, optional (default: False) If True, the assistant will automatically execute the code it generates.
    variables: dict, optional (default: None) A dictionary of variables that should be available to the assistant.
               If None, it will use the global variables of the current namespace.

    """
    from IPython.core.getipython import get_ipython
    Context.assistant = CustomAgent(model, temperature)
    Context.auto_execute = auto_execute

    if variables is None:
        p = get_ipython()
        Context.variables = p.user_ns
    else:
        Context.variables = variables

    if Context.verbose:
        print("Assistant initialised. You can now use it, e.g., copy and paste the"
          "below two lines into the next cell and execute it."
          "\n\n%%bob"
          "\nplease generate a noisy grayscale image containing 10 blurry blobs with a diameter of 20 pixels each.")
