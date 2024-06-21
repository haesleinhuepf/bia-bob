from IPython.core.magic import register_line_cell_magic
from ._utilities import keep_available_packages
import warnings

DEFAULT_MODEL = 'gpt-4o-2024-05-13'
DEFAULT_VISION_MODEL = 'gpt-4o-2024-05-13'
BLABLADOR_BASE_URL = 'https://helmholtz-blablador.fz-juelich.de:8000/v1'
OLLAMA_BASE_URL = 'http://localhost:11434/v1'

class Context:
    variables = None
    model = None
    vision_model = None
    verbose = False
    auto_execute = False
    chat = []
    client = None
    vision_client = None
    plugins_enabled = True
    seed = None # openai only
    temperature = None # openai only
    endpoint = None
    api_key = None

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
        "pyclesperanto_prototype",
        "apoc",
        "napari-segment-blobs-and-things-with-membranes",
        "napari-simpleitk-image-processing",
        "napari-skimage-regionprops",
        "skan",
        "aicsimageio",
        "os",
        "dask",
        "dask_image",
        "czifile",
        "cudf",
        "cupy",
        "pyclesperanto",
        "pathlib"
        # to add libraries here, add their pypi package names (not their import names)
    ])


def bob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and pastes the code into the next cell.
    """
    from IPython.core.getipython import get_ipython
    from IPython.display import display
    from ._utilities import generate_response_to_user, output_text, is_image, generate_response
    from ._notebook_generation import generate_notebook

    if Context.model is None:
        init_assistant()

    if line in Context.variables and is_image(Context.variables[line]):
        image = Context.variables[line]
    else:
        image = None

    user_input = combine_user_input(line, cell)

    if user_input is None:
        display("Please ask a question!")
        return

    TASK_TYPE_CODE_GENERATION = 1
    TASK_TYPE_TEXT_RESPONSE = 2
    TASK_TYPE_NOTEBOOK_GENERATION = 3
    TASK_TYPE_NOTEBOOK_MODIFICATION = 4

    task_selection_prompt = f"""
    Given the following prompt, decide which of the following types of tasks we need to perform:
    {TASK_TYPE_CODE_GENERATION}. Code generation: The prompt asks for code to be generated.
    {TASK_TYPE_TEXT_RESPONSE}. Text response: The prompt asks for a text response.    
    {TASK_TYPE_NOTEBOOK_GENERATION}. Notebook generation: The prompt asks explicitly for a notebook to be generated. Only choose this if the prompt explicitly asks for creating a new notebook.
    {TASK_TYPE_NOTEBOOK_MODIFICATION}. Notebook modification: The prompt asks for a modification of an existing notebook. Only choose this if the prompt explicitly asks for modifying an existing notebook and a notebook filename is given.
    
    This is the prompt:
    {user_input}
    
    Now, write the number of the task type into the next cell. Print the number only.
    """
    response = generate_response(chat_history=[],
                                image=None,
                                model=Context.model,
                                system_prompt="",
                                user_prompt=task_selection_prompt,
                                vision_system_prompt="")
    task_type = int(response.strip().strip("\n").split(".")[0])

    if task_type == TASK_TYPE_NOTEBOOK_GENERATION:
        code = None
        filename = generate_notebook(user_input, image=image)
        text = f"A notebook has been saved as [{filename}]({filename})."
    elif task_type == TASK_TYPE_NOTEBOOK_MODIFICATION:
        code = None
        filename = generate_notebook(user_input, modify_existing_notebook=True, image=image)
        text = f"The modified notebook has been saved as [{filename}]({filename})."
    else:
        code, text = generate_response_to_user(Context.model, user_input, image)

    # print out explanation
    if code is None or not Context.auto_execute:
        output_text(text)

    if code is not None:
        p = get_ipython()
        if Context.auto_execute:
            # replace the current cell that contained the prompt
            p.set_next_input(code, replace=True)
            # execute it
            p.run_cell(code)
        else:
            # put a new cell below the current cell
            p.set_next_input(code, replace=False)


try:
    register_line_cell_magic(bob)
except NameError:
    pass


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


def init_assistant(model=DEFAULT_MODEL, auto_execute:bool = False, variables:dict=None, endpoint=None, api_key=None,
                   vision_model=DEFAULT_VISION_MODEL, keep_history:bool=False, silent:bool=False):
    """Initialises the assistant.

    Parameters
    ----------
    model: str
    auto_execute: bool, optional (default: False) If True, the assistant will automatically execute the code it generates.
    variables: dict, optional (default: None) A dictionary of variables that should be available to the assistant.
               If None, it will use the global variables of the current namespace.
    endpint: str Custom endpoint, e.g. 'blablador'
    api_key: str API key for the custom endpoint
    vision_model: str, optional (default: 'gpt-4o-2024-05-13') The vision model to use.
    keep_history: bool, optional (default: False) If True, the chat history will be kept.
    silent: bool, optional (default: False) If True, the assistant will not print any messages after initializing.
    """
    from IPython.core.getipython import get_ipython
    from ._utilities import correct_endpoint
    Context.model = model
    Context.vision_model = vision_model
    Context.auto_execute = auto_execute
    Context.client = None
    Context.vision_client = None

    try:
        if variables is None:
            p = get_ipython()
            Context.variables = p.user_ns
        else:
            Context.variables = variables
    except:
        Context.variables = {}

    if not keep_history:
        Context.chat = []

    endpoint, api_key = correct_endpoint(endpoint, api_key)

    Context.endpoint = endpoint
    Context.api_key = api_key

    if Context.verbose:
        print("Assistant initialised. You can now use it, e.g., copy and paste the"
          "below two lines into the next cell and execute it."
          "\n\n%%bob"
          "\nplease generate a noisy grayscale image containing 10 blurry blobs with a diameter of 20 pixels each.")

    if not silent:
        from bia_bob import __version__ as version
        from IPython.display import display, HTML
        from ._utilities import version_string

        display(HTML(version_string(model, vision_model, endpoint, version)))


def enable_plugins(enabled: bool = True):
    Context.plugins_enabled = enabled
