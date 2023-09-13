def make_variable_name(name: str) -> str:
    name = name.replace(".", "_")
    name = name.replace("/", "_")
    name = name.replace("\\", "_")
    name = name.replace(" ", "_")
    name = name.replace(".", "_")

    while name.startswith("_"):
        name = name[1:]

    return name


def find_best_fit(options, search_for):
    import Levenshtein as lev

    best_ratio = -1
    best_value = None

    for option in options:
        ratio = lev.ratio(option, search_for)
        if ratio > best_ratio:
            best_ratio = ratio
            best_value = option
    return best_value

def is_image(potential_image):
    return hasattr(potential_image, "shape") and hasattr(potential_image, "dtype")


def find_image(variables, key):
    return find_variable(variables, key, is_image)


def is_dataframe(potential_dataframe):
    import pandas as pd
    return isinstance(potential_dataframe, pd.DataFrame)


def find_dataframe(variables, key):
    return find_variable(variables, key, is_dataframe)


def find_variable(variables, key, type_checker_function):
    from ._machinery import _context
    if key in variables.keys():
        return variables[key]

    other_name = make_variable_name(key)
    if other_name in variables.keys():
        return variables[other_name]

    other_name = find_best_fit([v for v in variables.keys() if type_checker_function(variables[v])], key)
    if _context.verbose:
        print("Searching for variable named ", other_name)
    return variables[other_name]


def generate_and_execute_code(task: str):
    """Useful for generating code for a specific task and executing it."""
    from ._machinery import _context

    # determine useful variables and functions in context
    variables = []
    functions = []
    for k, v in _context.variables.items():
        if k.startswith("_"):
            continue
        if callable(v):
            if k not in ["quit", "exit"]:
                functions.append(k)
            continue
        variables.append(k)

    libraries = {"skimage", "numpy", "scipy", "pandas", "matplotlib", "seaborn", "sklearn"}

    additional_hints = f"""
    Write high-quality python code.
    Use preferably the python libraries {",".join([str(v) for v in libraries])}.
    Show results and save them in variables.
    The following variables are available: {",".join([str(v) for v in variables])}
    Do not set the values of the variables that are available.
    The following functions are available: {",".join([str(v) for v in functions])}
    A live python environment is available and the code you produce will be executed afterwards.

    The code should do the following:
    """
    from ._utilities import generate_code
    from IPython.display import display, Markdown

    if _context.verbose:
        print("Code request:\n", additional_hints + task + "\n")

    code, full_response = generate_code(additional_hints + task)

    display(Markdown(full_response))

    if _context.verbose:
        print("Code response:\n", code)

    if _context.verbose:
        print("Execution:")

    exec(code, _context.variables)

    if _context.verbose:
        print("Execution done.")

    return "Code was generated and executed."


def generate_code(task):
    """Uses a language model to generate code that solves a given task."""
    full_response = prompt(task)

    modified_response = full_response.replace("```python", "```")

    potential_code_blocks = modified_response.split("```")

    if len(potential_code_blocks) == 1:
        code = potential_code_blocks[0]

    else:
        code = ""
        for i, code_block in enumerate(potential_code_blocks):
            if "pip install" in code_block or "conda install" in code_block:
                continue

            if i % 2 == 1:  # chatGPT commonly answers with text first and python code between ``` and ```
                code = code + code_block + "\n"

    return code, full_response


def prompt(message:str, model="gpt-4"):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    """
    import openai

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": message}]
    )
    return response['choices'][0]['message']['content']