from IPython.core.magic import register_line_cell_magic
from ._utilities import keep_available_packages, is_notebook

DEFAULT_MODEL = 'gpt-4o-2024-08-06'
DEFAULT_VISION_MODEL = 'gpt-4o-2024-08-06'
BLABLADOR_BASE_URL = 'https://helmholtz-blablador.fz-juelich.de:8000/v1'
OLLAMA_BASE_URL = 'http://localhost:11434/v1'
AZURE_BASE_URL = "https://models.inference.ai.azure.com"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DEFAULT_SYSTEM_PROMPT = """
You are a extremely talented bioimage analyst and you use Python to solve your tasks unless stated otherwise.
If there are several ways to solve the task, chose the option with the least amount of code.    

## Python specific instructions

When writing python code, you can only use those libraries: {libraries}.
If you create images, show the results and save them in variables for later reuse.
{reusable_variables}
NEVER overwrite the values of the variables and functions that are available.

## Python specific code snippets

If the user asks for those simple tasks, use these code snippets.

{additional_snippets}
{builtin_snippets}

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


class Context:
    variables = None
    model = None
    vision_model = None
    verbose = False
    chat = []
    client = None
    vision_client = None
    plugins_enabled = True
    seed = None # openai only
    temperature = None # openai only
    endpoint = None
    api_key = None
    system_prompt_template = DEFAULT_SYSTEM_PROMPT

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
        "pathlib",
        "bia-bob",
        "ipywidgets"
        # to add libraries here, add their pypi package names (not their import names)
    ])

# special case for pyclesperanto, replacing pyclesperanto_prototype:
if "pyclesperanto" in Context.libraries and "pyclesperanto_prototype" in Context.libraries:
    Context.libraries.remove("pyclesperanto_prototype")
if "pyclesperanto" in Context.libraries and "pyclesperanto-prototype" in Context.libraries:
    Context.libraries.remove("pyclesperanto-prototype")

def bob(line: str = None, cell: str = None):
    """Sends a prompt to openAI
    and shows the text and code response
    and pastes the code into the next cell.
    """
    from IPython.core.getipython import get_ipython
    from IPython.display import display
    from ._utilities import generate_response_to_user, output_text, is_image, ask_llm, refine_code
    from ._notebook_generation import generate_notebook, generate_file

    if Context.model is None:
        init_assistant()

    if line in Context.variables and is_image(Context.variables[line]):
        image = Context.variables[line]
        image_name = line
    else:
        image = None

    user_input = combine_user_input(line, cell)

    if user_input is None:
        display("Please ask a question!")
        return

    # replace {variable} with variable content
    try:
        user_input = user_input.format(**Context.variables)
    except:
        pass

    TASK_TYPE_OTHER = 1
    TASK_TYPE_CODE_GENERATION = 1
    TASK_TYPE_CODE_MODIFICATION = 2
    TASK_TYPE_TEXT_RESPONSE = 3
    TASK_TYPE_NOTEBOOK_GENERATION = 4
    TASK_TYPE_NOTEBOOK_MODIFICATION = 5
    TASK_TYPE_FILE_GENERATION = 6


    supported_file_types_for_generation = [".md", ".txt", ".csv", ".yml", ".yaml", ".json", ".py"]

    task_selection_prompt = f"""
    Given the following prompt, decide which of the following types of tasks we need to perform:
    {TASK_TYPE_CODE_GENERATION}. Code generation: The prompt asks for code to be generated.
    {TASK_TYPE_CODE_MODIFICATION}. Code modification: The prompt asks for given code to be modified.
    {TASK_TYPE_TEXT_RESPONSE}. Text response: The prompt asks for a text response.    
    {TASK_TYPE_NOTEBOOK_GENERATION}. Notebook generation: The prompt asks explicitly for a notebook to be generated. Only choose this if the prompt explicitly asks for creating a new notebook.
    {TASK_TYPE_NOTEBOOK_MODIFICATION}. Notebook modification: The prompt asks for a modification of an existing notebook. Only choose this if the prompt explicitly asks for modifying an existing notebook and a) a notebook filename is given or b) the current notebook is mentioned.
    {TASK_TYPE_FILE_GENERATION}. File generation: The prompt asks for a file to be generated. Only choose this if the prompt explicitly asks for creating a new file ending with any of those extensions: {",".join(supported_file_types_for_generation)}.
    {TASK_TYPE_OTHER}. Other: If you're not sure or if the prompt does not fit into any of the above categories.
    
    This is the prompt:
    {user_input}
    
    Now, write the number of the task type into the next cell. Print the number only.
    """
    response = ask_llm(task_selection_prompt)

    try:
        task_type = int(response.strip().strip("\n").split(".")[0])
    except:
        task_type = TASK_TYPE_OTHER

    if task_type == TASK_TYPE_FILE_GENERATION:
        task_type = TASK_TYPE_OTHER
        # make sure only supported file formats
        for ending in supported_file_types_for_generation:
            if ending in user_input:
                task_type = TASK_TYPE_FILE_GENERATION
                break
    if task_type == TASK_TYPE_FILE_GENERATION:
        task_type = TASK_TYPE_OTHER
        keywords = ["write", "generate", "create"]
        for keyword in keywords:
            if keyword in user_input.lower():
                task_type = TASK_TYPE_FILE_GENERATION
                break


    if task_type == TASK_TYPE_NOTEBOOK_GENERATION:
        code = None
        filename = generate_notebook(user_input, image=image)
        if is_notebook():
            text = f"A notebook has been saved as [{filename}]({filename})."
        else:
            text = f"The file has been saved as {filename}. You can open it using:\n\n    jupyter lab {filename}\n\n"
    elif task_type == TASK_TYPE_NOTEBOOK_MODIFICATION:
        code = None
        filename = generate_notebook(user_input, modify_existing_notebook=True, image=image)
        if is_notebook():
            text = f"The modified notebook has been saved as [{filename}]({filename})."
        else:
            text = f"The file has been saved as {filename}. You can open it using:\n\n    jupyter lab {filename}\n\n"
    elif task_type == TASK_TYPE_FILE_GENERATION:
        code = None
        filename = generate_file(user_input, image=image)
        if is_notebook():
            text = f"The file has been saved as [{filename}]({filename})."
        else:
            text = f"The file has been saved as {filename}. You can open it using:\n\n    jupyter lab {filename}\n\n"
    else: # TASK_TYPE_CODE_MODIFICATION or TASK_TYPE_CODE_GENERATION
        if task_type == TASK_TYPE_CODE_MODIFICATION:
            user_input = user_input + "\n\nReturn the complete code. Keep the code modifications minimal. Do not drop imports or functions which are still needed."
        code, text = generate_response_to_user(Context.model, user_input, image)

        if image is not None:
            # we need to add this information to the history.
            Context.chat.append({
                "role": "user",
                "content": f"Assume there is an image stored in variable `{image_name}`. The image can be described like this: {text}. Just confirm this with 'ok'."
            })
            Context.chat.append({
                "role": "assistant",
                "content": "ok"
            })

    # print out explanation
    output_text(text)

    if code is not None and task_type != TASK_TYPE_CODE_MODIFICATION:
        code = refine_code(code)

    if code is not None:
        p = get_ipython()

        # put a new cell below the current cell
        if p is not None:
            p.set_next_input(code, replace=task_type == TASK_TYPE_CODE_MODIFICATION)
        else:
            print(code)


try:
    register_line_cell_magic(bob)
except NameError:
    pass


try:
    from IPython.core.inputtransformer import InputTransformer


    class MyTextTransformer(InputTransformer):
        
        def __call__(self, line):
            return self.push(line)
        
        def push(self, lines):
            from IPython import get_ipython
            from ._utilities import generate_response_to_user

            mode = "none"
            if any(["%bob" in line for line in lines]):
                if lines[0].startswith("%%bob") or lines[0].startswith("%bob"):
                    return lines
                mode = "complete"
            elif lines[-1].strip().endswith("%fix"):
                mode = "fix"
            elif lines[-1].strip().endswith("%doc"):
                mode = "doc"
            else:
                return lines
            
            lines[-1] = lines[-1].replace("%%fix", "").replace("%fix", "").replace("%%doc", "").replace("%doc", "")

            from bia_bob import ask_llm
            text = "\n".join(lines)

            if mode == "complete":
                prompt = f"""Please complete the following code by replacing "%bob" with the respective code.

        ```python
        {text}
        ```
        Provide the completed code.
        """
                if Context.model is None:
                    init_assistant()

                p = get_ipython()
                
                code, text = generate_response_to_user(Context.model, prompt)

                # replace the code in the current cell
                if p is not None:
                    p.set_next_input(code, replace=True)
            elif mode == "fix":
                from ._bug_fixing import fix
                fix(code)
            elif mode == "doc":
                from ._document import doc
                doc(code)
            # execute no code
            return [] 

        def reset(self):
            pass

    def register_input_transformer():
        from IPython import get_ipython

        ip = get_ipython()
        ip.input_transformers_cleanup.append(MyTextTransformer())

    register_input_transformer()
except:
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


def init_assistant(model=None, auto_execute:bool = False, variables:dict=None, endpoint=None, api_key=None,
                   vision_model=None, keep_history:bool=False, silent:bool=False, system_prompt=None):
    """Initialises the assistant.

    Parameters
    ----------
    model: str
    auto_execute: bool, optional (default: False) If True, the assistant will automatically execute the code it generates.
    variables: dict, optional (default: None) A dictionary of variables that should be available to the assistant.
               If None, it will use the global variables of the current namespace.
    endpint: str Custom endpoint, e.g. 'blablador'
    api_key: str API key for the custom endpoint
    vision_model: str, optional (default: 'gpt-4o-2024-08-06') The vision model to use.
    keep_history: bool, optional (default: False) If True, the chat history will be kept.
    silent: bool, optional (default: False) If True, the assistant will not print any messages after initializing.
    """
    from IPython.core.getipython import get_ipython
    from ._utilities import correct_endpoint
    import os
    import yaml
    from bia_bob import __version__ as version

    # setup default config
    config = {
        "model": DEFAULT_MODEL,
        "vision_model": DEFAULT_VISION_MODEL,
        "endpoint": None,
        "system_prompt": DEFAULT_SYSTEM_PROMPT
    }

    # load config from disk
    home_dir = os.path.expanduser('~')
    config_filename = os.path.join(home_dir, ".cache", "bia-bob", f"config_bia_bob_{version}.yaml")
    os.makedirs(os.path.dirname(config_filename), exist_ok=True)
    if os.path.exists(config_filename):
        with open(config_filename, mode="rt", encoding="utf-8") as test_df_to_yaml:
            config = yaml.full_load(test_df_to_yaml)

    # change to default config if parameters are not given
    if model is None and vision_model is None and endpoint is None:
        model = config["model"]
        vision_model = config["vision_model"]
        endpoint = config["endpoint"]
    if system_prompt is None:
        if "system_prompt" in config.keys():
            system_prompt = config["system_prompt"]
        else:
            system_prompt = DEFAULT_SYSTEM_PROMPT

    # store config to disk
    config["model"] = model
    config["vision_model"] = vision_model
    config["endpoint"] = endpoint
    config["system_prompt"] = system_prompt
    with open(config_filename, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

    Context.model = model
    Context.vision_model = vision_model
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
    Context.system_prompt_template = system_prompt

    if Context.verbose:
        print("Assistant initialised. You can now use it, e.g., copy and paste the"
          "below two lines into the next cell and execute it."
          "\n\n%%bob"
          "\nplease generate a noisy grayscale image containing 10 blurry blobs with a diameter of 20 pixels each.")

    if not silent:
        from bia_bob import __version__ as version
        from IPython.display import display, HTML
        from ._utilities import version_string

        if is_notebook():
            remark = version_string(model, vision_model, endpoint, version) + ". " + disclaimer(html=True)
            display(HTML(f"""
            <div style="font-size:7pt">
            This notebook may contain text, code and images generated by artificial intelligence.
            {remark}
            </div>
            """))
        else:

            remark = version_string(model, vision_model, endpoint, version) + ". " + disclaimer()
            print("bia-bob is using artificial intelligence to generate text, code and images.")
            print(remark)


def disclaimer(html=False):
    if html:
        return "Do not enter sensitive or private information and verify generated contents according to good scientific practice. Read more: <a href=\"https://github.com/haesleinhuepf/bia-bob#disclaimer\">https://github.com/haesleinhuepf/bia-bob#disclaimer</a>"
    else:
        return "Do not enter sensitive or private information and verify generated contents according to good scientific practice. Read more: https://github.com/haesleinhuepf/bia-bob#disclaimer"


def enable_plugins(enabled: bool = True):
    Context.plugins_enabled = enabled
