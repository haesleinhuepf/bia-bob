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
    from ._machinery import Context
    if key in variables.keys():
        return variables[key]

    other_name = make_variable_name(key)
    if other_name in variables.keys():
        return variables[other_name]

    other_name = find_best_fit([v for v in variables.keys() if type_checker_function(variables[v])], key)
    if Context.verbose:
        print("Searching for variable named ", other_name)
    return variables[other_name]


def generate_response(user_input: str, model):
    """Generates code and text respond for a specific user input.
    To do so, it combines the user input with additional context such as
    current variables and a prompt template."""

    from ._machinery import Context

    # determine useful variables and functions in context
    variables = []
    functions = []
    for key, value in Context.variables.items():
        if key.startswith("_"):
            continue
        if callable(value):
            if key not in ["quit", "exit"]:
                functions.append(key)
            continue
        variables.append(key)

    libraries = {"skimage", "numpy", "scipy", "pandas", "matplotlib", "seaborn", "sklearn"}

    additional_hints = f"""
    If the request entails writing code, write concise professional 
    bioimage analysis high-quality python code.
    The code should be as short as possible.
    If there are several ways to solve the task, chose the option with the least amount of code.
    Preferably, use these python libraries {",".join([str(v) for v in libraries])}.
    Show results and save them in variables.
    The following variables are available: {",".join([str(v) for v in variables])}
    Do not set the values of the variables that are available.
    The following functions are available: {",".join([str(v) for v in functions])}
    A live python environment is available and the code you produce will be executed afterwards.

    Before writing the code, provide a concise step-by-step plan 
    of what the code will be going to do. 
    This plan must not contain any "`" characters and should be written in plain text.
    Then print the code.
    The code block must start with the line: 
    ```python
    and it must end with the line:
    ```
    There must be no text after the code block.
    
    If the user request does not require to write code, simply answer in plain text.
    
    Here is the user request:
    """

    if Context.verbose:
        print("\nPrompt:", additional_hints + user_input)

    from ._utilities import generate_answer_to_full_prompt
    code, text = generate_answer_to_full_prompt(additional_hints + user_input, model)

    return code, text


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


def generate_answer_to_full_prompt(full_prompt, model):
    """Uses a language model to generate a response to a given prompt
     and returns both the text and executable code response."""
    full_response = generate_response_from_openai(full_prompt, model)

    from ._machinery import Context
    if Context.verbose:
        print("\n\nFull response:\n", full_response)

    # Define the pattern
    import re
    pattern = re.compile(r'([\s\S]*?)```python([\s\S]*?)```')

    # Search for the pattern in the text
    match = pattern.search(full_response)

    if match:
        text = match.group(1).strip()
        code = match.group(2).strip()
    else:
        text = full_response
        code = None

    text = "#### Assistant response\n\n" + text
    text = text + "\n#### Additional information\n\n"

    import tiktoken
    encoding = tiktoken.encoding_for_model(model)
    text = text + "The input prompt contained " + str(len(encoding.encode(full_prompt))) + " tokens.  "
    text = text + "The response contained " + str(len(encoding.encode(full_response))) + " tokens.  "

    return code, text


def generate_response_from_openai(full_prompt: str, model="gpt-4"):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    """
    import openai

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": full_prompt}]
    )
    return response['choices'][0]['message']['content']


def available_models():
    import openai
    models = openai.Model.list()
    for model in models['data']:
        print(model['id'])
