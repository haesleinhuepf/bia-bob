import warnings
from functools import lru_cache

def ask_llm(prompt, image=None, chat_history=None):
    """Ask the language model a simple question and return the response."""
    from ._machinery import Context, init_assistant
    if Context.model is None:
        init_assistant()

    if chat_history is None:
        chat_history = []

    return generate_response(chat_history=chat_history,
                      image=image,
                      model=Context.model,
                      system_prompt="",
                      user_prompt=prompt,
                      vision_system_prompt="")


def generate_response_to_user(model, user_prompt: str, image=None, additional_system_prompt: str = None, max_number_attempts:int = 3, system_prompt:str=None):
    """Generates code and text respond for a specific user input.
    To do so, it combines the user input with additional context such as
    current variables and a prompt template."""
    from ._machinery import Context

    text, plan, code = None, None, None

    chat_backup = [c for c in Context.chat]

    for attempt in range(1, max_number_attempts + 1):
        if system_prompt is None:
            system_prompt = create_system_prompt()
        if additional_system_prompt is not None:
            system_prompt += "\n" + additional_system_prompt

        vision_system_prompt = create_vision_system_prompt()

        # take the last n chat entries
        n = 10
        chat_history = Context.chat[-n:]

        if Context.verbose:
            print("\nUser prompt:", user_prompt)
            print("\nSystem prompt:", system_prompt)
            print_chat(chat_history)

        full_response = generate_response(chat_history, image, model, system_prompt, user_prompt, vision_system_prompt)
        Context.chat = chat_history

        if Context.verbose:
            print("\n\nFull response:\n", full_response)



        # split response in text and code
        text, plan, code = split_response(full_response)

        if text is not None and plan is not None and code is None:
            text = text + "\n\n" + plan
            break

        if text is None and code is None:
            text = full_response
            break

        if text is not None and plan is not None:
            break

        if image is not None:
            break

        print(f"There was an issue. Retrying ({attempt}/{max_number_attempts})...")
        Context.chat = chat_backup

    return code, text


def generate_response(chat_history, image, model, system_prompt, user_prompt, vision_system_prompt):
    from ._machinery import Context
    from .endpoints._openai import generate_response_from_openai
    from .endpoints._googlevertex import generate_response_from_vertex_ai, generate_response_from_google_ai
    from .endpoints._anthropic import generate_response_from_anthropic
    from .endpoints._azure import generate_response_from_azure
    from .endpoints._mistral import generate_response_from_mistral

    if (Context.endpoint == "github_models" or Context.endpoint == "azure") and "gpt-" not in model and "o1-" not in model and "mistral" not in model:
        full_response = generate_response_from_azure(model, system_prompt, user_prompt, chat_history, image,
                                                      base_url=Context.endpoint, api_key=Context.api_key,
                                                      vision_model=Context.vision_model,
                                                      vision_system_prompt=vision_system_prompt)
    elif "mistral" in model or (Context.vision_model is not None and "pixtral" in Context.vision_model and image is not None):
        full_response = generate_response_from_mistral(model, system_prompt, user_prompt, chat_history, image,
                                                      base_url=Context.endpoint, api_key=Context.api_key,
                                                      vision_model=Context.vision_model,
                                                      vision_system_prompt=vision_system_prompt)

    elif Context.endpoint is not None:
        full_response = generate_response_from_openai(model, system_prompt, user_prompt, chat_history, image,
                                                      base_url=Context.endpoint, api_key=Context.api_key,
                                                      vision_model=Context.vision_model,
                                                      vision_system_prompt=vision_system_prompt)
    elif "gpt-" in model:
        full_response = generate_response_from_openai(model, system_prompt, user_prompt, chat_history, image,
                                                      vision_model=Context.vision_model,
                                                      vision_system_prompt=vision_system_prompt)
    elif model == "gemini" or model == "gemini-pro" or model == "gemini-pro-vision":
        import warnings
        warnings.warn(f"The model {model} is deprecated. Consider using gemini-1.5-flash or gemini-1.5-pro instead.")
        full_response = generate_response_from_vertex_ai(model, system_prompt, user_prompt, chat_history, image,
                                                         vision_model=Context.vision_model,
                                                         vision_system_prompt=vision_system_prompt)
    elif "gemini" in model:
        full_response = generate_response_from_google_ai(model, system_prompt, user_prompt, chat_history, image,
                                                         vision_model=Context.vision_model,
                                                         vision_system_prompt=vision_system_prompt)
    elif model.startswith("claude"):
        full_response = generate_response_from_anthropic(model, system_prompt, user_prompt, chat_history, image,
                                                      vision_model=Context.vision_model,
                                                      vision_system_prompt=vision_system_prompt)
    else:
        raise RuntimeError(f"Unknown model API for {model}")
    return full_response


def split_response(text):
    backup_text = text
    text = text \
        .replace("```python", "```") \
        .replace("```Python", "```") \
        .replace("```nextflow", "```") \
        .replace("```java", "```") \
        .replace("```javascript", "```") \
        .replace("```macro", "```") \
        .replace("```groovy", "```") \
        .replace("```jython", "```") \
        .replace("```md", "```") \
        .replace("```markdown", "```") \
        .replace("```txt", "```") \
        .replace("```csv", "```") \
        .replace("```yml", "```") \
        .replace("```yaml", "```") \
        .replace("```json", "```") \
        .replace("```py", "```")

    # hotfix modifications for not-so-capable models (e.g. ollama/codellama or blablador/Mistral-7B-Instruct-v0.2)
    for item in ["Summary", "Plan", "Code"]:
        text = "\n" + text
        text = text.replace(f"\n# {item}", f"\n### {item}")
        text = text.replace(f"\n## {item}", f"\n### {item}")
        text = text.replace(f"\n### {item}:", f"\n### {item}")

    # Split the text based on three predefined Markdown headlines
    import re
    sections = re.split(r'### (Summary|Plan|Code)\s*', text)

    # The first element is usually an empty string before the first headline
    # The rest of the elements are alternating between section names and contents
    summary, plan, code = None, None, None
    for i in range(1, len(sections), 2):
        if sections[i] == 'Summary':
            summary = sections[i + 1]
        elif sections[i] == 'Plan':
            plan = sections[i + 1]
        elif sections[i] == 'Code':
            code = sections[i + 1]

    if summary is None and plan is None and code is None and "```python" in backup_text:
        # second attempt
        pattern = r"```python\n(.*?)\n```"
        code_blocks = re.findall(pattern, backup_text, re.DOTALL)
        code = "\n".join(code_blocks)
        summary = backup_text.split("```python")[0]
        plan = ""
        return summary, plan, code

    if code is not None:
        original_code = code
        parts = code.split("```")
        if len(parts) == 1:
            code = None
        else:
            text = ""
            code = ""
            for t, c in zip(parts[::2], parts[1::2]):
                code = code + c
            code = code.strip("\n")

        if code is None or len(code) == 0:
            code = original_code

    return summary, plan, code


@lru_cache(maxsize=1)
def generate_code_samples():
    """Load code snippets from built-in suggestions and plugins."""
    from ._machinery import Context
    import importlib
    import os

    snippets = []

    # load built-in suggestions:
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), "suggestions")):
        if filename.startswith("_") and filename.endswith(".py"):
            module = filename[1:-3]
            original_module_name = module
            if module in Context.libraries or module.replace("_", "-") in Context.libraries:
                pass
            else:
                continue

            loaded_module = importlib.import_module(f"bia_bob.suggestions._{original_module_name}")
            func = getattr(loaded_module, f"suggestions")
            snippets.append(func())
    snippets = "\n".join(snippets)

    # load plugin suggestions
    if Context.plugins_enabled:
        from importlib.metadata import entry_points

        # Discover all bia-bob plugins\
        try:
            bia_bob_plugins = entry_points(group='bia_bob_plugins')
        except TypeError:
            all_plugins = entry_points()
            try:
                bia_bob_plugins = all_plugins['bia_bob_plugins']
            except KeyError:
                bia_bob_plugins = []

        additional_instructions = []
        # Iterate over discovered entry points and load them
        for ep in bia_bob_plugins:
            instructions = ""
            
            try:
                func = ep.load()

                # load instructions from a plugin
                instructions = func()
            except:
                # do not crash if plugins are crashing
                print("error")
                pass

            # special treatment for code snippets from stackview, as it won't work with the custom kernel
            if "stackview" not in instructions or "stackview" in Context.libraries:
                additional_instructions.append(instructions)

        additional_snippets = "\n".join(additional_instructions)
    else:
        additional_snippets = ""

    additional_snippets = shorten_text(additional_snippets)

    return shorten_text(snippets), shorten_text(additional_snippets)


def shorten_text(text):
    while (" \n" in text):
        text = text.replace(" \n", "\n")

    while ("\n\n\n" in text):
        text = text.replace("\n\n\n", "\n\n")

    return text

def create_system_prompt(reusable_variables_block=None):
    """Creates a system prompt that contains instructions of general interest, available functions and variables."""
    from ._machinery import Context

    # determine useful variables and functions in context
    if reusable_variables_block is None:
        reusable_variables_block = create_reusable_variables_block()
    else:
        warnings.warn("Deprecated use of create_system_prompt with reusable_variables_block. Do not pass this parameter to make your code work mid/long-term.")

    snippets, additional_snippets = generate_code_samples()
    libraries = Context.libraries

    system_prompt = f"""
    You are a extremely talented bioimage analyst and you use Python to solve your tasks unless stated otherwise.
    If there are several ways to solve the task, chose the option with the least amount of code.    
    
    ## Python specific instructions
    
    When writing python code, you can only use those libraries: {",".join([str(v) for v in libraries])}.
    If you create images, show the results and save them in variables for later reuse.
    {reusable_variables_block}
    NEVER overwrite the values of the variables and functions that are available.
    
    ## Python specific code snippets
    
    If the user asks for those simple tasks, use these code snippets.
    
    {additional_snippets}
    {snippets}
    
    ## Todos
    
    Answer your response in three sections:
    1. Summary: First provide a short summary of the task.
    2. Plan: Provide a concise step-by-step plan without any code.
    3. Code: Provide the code.
    
    Structure it with markdown headings like this:
    
    ### Summary
    I will do this and that.
    
    ### Plan
    1. Do this.
    2. Do that.
    
    ### Code
    ```
    this()
    that()
    ```
    
    ## Final remarks
    
    The following points have highest importance and may overwrite the instructions above.
    Make sure to provide 1) summary, 2) plan and 3) code.
    Make sure to keep your answer concise and to the point. Make sure the code you write is correct and can be executed.
    """

    return system_prompt


def create_vision_system_prompt():
    vision_system_prompt = """
    Describe the given image. Assume it is a scientific image resulting from imaging devices such as microscope, clinical scanners or other kinds of detectors.
    Consider describing the image's background (bright, dark, homogeneous, inhomogeneous) and forgreound (blobs, meshes, membranes, cells, subcellular structures, crystals, etc.)
    Describe the image's quality (resolution, noise, artifacts, etc.)
    Describe the image's content (how many objects, large, small objects, etc.)
    """
    return vision_system_prompt


def create_reusable_variables_block():
    """Creates a block of text that explains which variables, functions and libraries are
    available to be used."""
    variables = []
    functions = []
    modules = []
    from ._machinery import Context
    import types

    # figure out which variables are not private
    for key, value in Context.variables.items():
        if key.startswith("_"):
            continue
        if callable(value):
            if key not in ["quit", "exit", "get_ipython", "open", "bob"]:
                functions.append(key)
            continue
        if isinstance(value, types.ModuleType):
            if key != "bia_bob":
                modules.append(key)
            continue
        if key in ["In", "Out"]:
            continue
        variables.append(key)

    return f"""
    The following variables are defined: {",".join([str(v) for v in variables])}    
    The following functions are defined: {",".join([str(v) for v in functions])}    
    The following modules or aliases are imported: {",".join([str(v) for v in modules])}
    """


def print_chat(chat):
    print("\nChat history:")
    for message in chat:
        role = message['role']
        content = message['content']
        print(role)
        print(content)


def output_text(text):
    """Display markdown content in the notebook."""
    if is_notebook():
        from IPython.display import display, Markdown
        display(Markdown(text))
    else:
        print(text)
    

def is_notebook() -> bool:
    """Returns true if the code is currently executed in a Jupyter notebook."""
    # adapted from: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
    from IPython.core.getipython import get_ipython

    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def numpy_to_bytestream(data):
    """Turn a NumPy array into a bytestream"""
    import numpy as np
    from PIL import Image
    import io

    # Convert the NumPy array to a PIL Image
    image = Image.fromarray(data.astype(np.uint8)).convert("RGBA")

    # Create a BytesIO object
    bytes_io = io.BytesIO()

    # Save the PIL image to the BytesIO object as a PNG
    image.save(bytes_io, format='PNG')

    # return the beginning of the file as a bytestream
    bytes_io.seek(0)
    return bytes_io.read()


def image_to_url(image):
    import base64
    from stackview._image_widget import _img_to_rgb

    rgb_image = _img_to_rgb(image)
    byte_stream = numpy_to_bytestream(rgb_image)
    base64_image = base64.b64encode(byte_stream).decode('utf-8')
    return f"data:image/png;base64,{base64_image}"


def is_image(potential_image):
    """Returns true if the given object is a numpy-compatible image/array."""
    return hasattr(potential_image, "shape") and hasattr(potential_image, "dtype")


def correct_endpoint(endpoint, api_key):
    import os
    from ._machinery import BLABLADOR_BASE_URL, OLLAMA_BASE_URL, AZURE_BASE_URL
    if endpoint == 'blablador':
        endpoint = BLABLADOR_BASE_URL
        if api_key is None:
            api_key = os.environ.get('BLABLADOR_API_KEY')
    elif endpoint == 'ollama':
        endpoint = OLLAMA_BASE_URL
    elif endpoint == "azure":
        endpoint = AZURE_BASE_URL
        if api_key is None:
            api_key = os.environ.get('AZURE_API_KEY')

    elif endpoint == "github_models":
        endpoint = AZURE_BASE_URL
        if api_key is None:
            api_key = os.environ.get('GH_MODELS_API_KEY')

    return endpoint, api_key


def available_models(endpoint=None, api_key=None):
    """Returns a list of available model names"""
    endpoint, api_key = correct_endpoint(endpoint, api_key)

    models = []
    if endpoint is None or endpoint == 'openai':
        try:
            from openai import OpenAI
            client = OpenAI()
            models = models + [model.id for model in client.models.list().data]
        except:
            print("Error while adding OpenAI models")
            pass

    if endpoint is None or endpoint == 'gemini':
        try:
            from vertexai.preview.generative_models import GenerativeModel
            models.append("gemini-pro")
            models.append("gemini-pro-vision")
        except:
            print("Error while adding VertexAI models")
            pass

    if endpoint is not None:
        from openai import OpenAI
        client = OpenAI()
        client.base_url = endpoint
        client.api_key = api_key
        models = models + [model.id for model in client.models.list().data]

    return sorted(models)


def keep_available_packages(libraries):
    """Goes through a given list of package names and return those that are installed on the system."""
    try:
        # Python 3.8+
        from importlib.metadata import distributions
    except ImportError:
        # Python < 3.8
        from importlib_metadata import distributions

    installed = [dist.metadata['Name'] for dist in distributions()]

    # add always available packages
    installed.append('os')

    result = [i for i in libraries if i in installed]

    return result


def version_string(model, vision_model, endpoint, version):
    return f"""Used model: {model}, vision model: {vision_model}, endpoint: {endpoint}, bia-bob version: {version}."""


def remove_outer_markdown_annotation(code):
    """In case code is wrapped in markdown annotations / code quotations, remove them. Returns the code only"""
    for subheader in ["Code", "Plan", "Summary"]:
        if "#" + subheader not in code:
            code = code + f"\n\n### {subheader}\n" + code

    _, _, new_code = split_response(code)

    return new_code


def refine_code(code):
    """Uses reflection to figure out which variables are available and imports are missing.
    The LLM is asked to refine the code accordingly."""
    if "%bob" in code:
        # task was to write a prompt
        return code
    original_code = code

    try:
        import pyclesperanto
        prototype = ""
    except:
        prototype = "_prototype"

    reusable_variables_block = create_reusable_variables_block()
    refined_code = ask_llm(f"""
    
    Given a list of available variables, functions and modules:
    {reusable_variables_block}
    
    Modify the following code:
    ```python
    {code}
    ```
    
    Update the code and make sure the following conditions are met:
    * The code imports all necessary functions and modules, except available functions and modules.
    * Do not overwrite variables, if the arey in the list of defined variables.
    * Do not make up modules when importing them.
    * Do NOT replace values such as filenames with variables.
    
    Return the code only.
    """)

    result = remove_outer_markdown_annotation(refined_code)

    result = result.replace("import cle", f"import pyclesperanto{prototype} as cle")
    result = result.replace("from stackview import stackview", "import stackview")

    if result is None:
        return original_code
    return result
