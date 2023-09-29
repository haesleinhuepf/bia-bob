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


def generate_response(input: str):
    """Generates code and text respond for a specific user input.
    To do so, it combines the user input with additional context such as
    current variables and a prompt template."""

    from ._machinery import _context

    # determine useful variables and functions in context
    variables = []
    functions = []
    for key, value in _context.variables.items():
        print(key)
        if key.startswith("_"):
            continue
        if callable(value):
            if key not in ["quit", "exit"]:
                functions.append(key)
            continue
        variables.append(key)

    libraries = {"skimage", "numpy", "scipy", "pandas", "matplotlib", "seaborn", "sklearn"}

    additional_hints = f"""
    Write concise professional bioimage analysis high-quality python code.
    The code should be as short as possible.
    If there are several ways to solve the task, chose the option with the least amount of code.
    Use preferably the python libraries {",".join([str(v) for v in libraries])}.
    Show results and save them in variables.
    The following variables are available: {",".join([str(v) for v in variables])}
    Do not set the values of the variables that are available.
    The following functions are available: {",".join([str(v) for v in functions])}
    A live python environment is available and the code you produce will be executed afterwards.

    The code block must start with the line
    ```python
    and it must end with the line 
    ```

    Before writing the code, provide a concise step-by-step plan.
    This plan must not contain any "`" characters!
    
    The python code should do the following:
    """

    if _context.verbose:
        print("\nPrompt:", additional_hints + input)

    from ._utilities import generate_answer_to_full_prompt
    code, full_response = generate_answer_to_full_prompt(additional_hints + input)

    if _context.verbose:
        print("\nCode:\n", code)

    return code, full_response


def output_text(text):
    """Display markdown content in the notebook."""
    from IPython.display import display, Markdown
    display(Markdown(text))

def output_code(code):
    """Display code content in the notebook."""
    from IPython.display import display, Markdown
    from IPython.core.display import HTML

    display(HTML(f"""
    <details>
    <summary> Show code </summary>
    <pre>
    {code}
    </pre>
    </details>
    """))


def generate_answer_to_full_prompt(task):
    """Uses a language model to generate a reponse to a given task
     and returns both the full response and also only the executable python code."""
    full_response = prompt(task)

    from ._machinery import _context
    if _context.verbose:
        print("\nFull response:\n", full_response)

    # Define the pattern
    import re
    pattern = re.compile(r'```python([\s\S]*?)```')

    # Search for the pattern in the text
    match = pattern.search(full_response)

    if match:
        code = match.group(1).strip()
    else:
        code = None

    #modified_response = full_response.replace("```python", "```")

    #potential_code_blocks = modified_response.split("```")

    # print("")
    #
    # if len(potential_code_blocks) == 1:
    #     code = potential_code_blocks[0]
    # else:
    #     code = ""
    #     for i, code_block in enumerate(potential_code_blocks):
    #         if "pip install" in code_block or "conda install" in code_block:
    #             continue
    #
    #         if i % 2 == 1:  # chatGPT commonly answers with text first and python code between ``` and ```
    #             code = code + code_block + "\n"

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