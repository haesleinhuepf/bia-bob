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


def generate_response_to_user(model, user_prompt: str):
    """Generates code and text respond for a specific user input.
    To do so, it combines the user input with additional context such as
    current variables and a prompt template."""

    system_prompt = create_system_prompt()

    # take the last ten entries
    from ._machinery import Context
    chat_history = Context.chat[-10:]

    if Context.verbose:
        print("\nUser prompt:", user_prompt)
        print("\nSystem prompt:", system_prompt)
        print("\nChat history:", print_chat(chat_history))

    code, text = generate_response_to_system_user_chat(model, system_prompt, user_prompt, chat_history)

    return code, text


def create_system_prompt():
    # determine useful variables and functions in context
    variables = []
    functions = []
    from ._machinery import Context
    for key, value in Context.variables.items():
        if key.startswith("_"):
            continue
        if callable(value):
            if key not in ["quit", "exit"]:
                functions.append(key)
            continue
        variables.append(key)
    libraries = {"skimage", "numpy", "scipy", "pandas", "matplotlib", "seaborn", "sklearn"}
    system_prompt = f"""
    If the request entails writing code, write concise professional bioimage analysis high-quality python code.
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
    If the request does not require to write code, simply answer in plain text.
    """
    return system_prompt


def print_chat(chat):
    for message in chat:
        role = message['role']
        content = message['content']

        # Limiting the content to first 100 characters
        # and appending "..." if the content is longer
        content = content[:100] + '...' if len(content) > 50 else content

        print(f"{role}: {content}")


def output_text(text):
    """Display markdown content in the notebook."""
    from IPython.display import display, Markdown
    display(Markdown(text))


def output_code(code):
    """Display code content in the notebook."""
    from IPython.display import display
    from IPython.core.display import HTML

    display(HTML(f"""
    <details>
    <summary> Show code </summary>
    <pre>
    {code}
    </pre>
    </details>
    """))


def generate_response_to_system_user_chat(model: str, system_prompt, user_prompt, chat_history):
    """Uses a language model to generate a response to a given prompt
     and returns both the text and executable code response."""
    full_response = generate_response_from_openai(model, system_prompt, user_prompt, chat_history)

    from ._machinery import Context
    if Context.verbose:
        print("\n\nFull response:\n", full_response)

    # Define the code pattern
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

    text = "### Assistant response\n\n" + text
    text += "\n#### Additional information\n\n"

    return code, text


def generate_response_from_openai(model: str, system_prompt: str, user_prompt: str, chat_history):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    """
    import openai

    system = [{"role": "system", "content": system_prompt}]
    user = [{"role": "user", "content": user_prompt}]

    response = openai.ChatCompletion.create(
        messages=system + chat_history + user,
        model=model)  # stream=True would be nice

    reply = response['choices'][0]['message']['content']

    from ._machinery import Context
    Context.chat += user + [{"role": "assistant", "content": reply}]

    # TODO: return also input and output tokens and compute the corresponding text
    #  in the calling function
    # import tiktoken
    # from ._machinery import Models
    # encoding = tiktoken.encoding_for_model(model)
    # input_token = len(encoding.encode(full_prompt))
    # output_token = len(encoding.encode(full_response))
    # details = "\n##### Request details\n\n"
    # details += "- Model: " + model + "\n"
    # details += "- Pricing: https://openai.com/pricing\n"
    # details += "- Input: " + str(input_token) + " token = "
    # input_price = Models.usd_per_1k_input_token(model) * input_token / 10.0
    # details += "{:.4f}".format(input_price) + " US Cent.\n"
    # details += "- Output: " + str(output_token) + " token = "
    # output_price = Models.usd_per_1k_output_token(model) * output_token / 10.0
    # details += "{:.4f}".format(output_price) + " US Cent.\n "
    # details += "\n"
    # text = details + text

    return reply


def available_models():
    import openai
    models = openai.Model.list()
    for model in models['data']:
        print(model['id'])
