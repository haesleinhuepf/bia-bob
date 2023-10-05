def generate_response_to_user(model, user_prompt: str):
    """Generates code and text respond for a specific user input.
    To do so, it combines the user input with additional context such as
    current variables and a prompt template."""

    system_prompt = create_system_prompt()

    # take the last n chat entries
    from ._machinery import Context
    n = 10
    chat_history = Context.chat[-n:]

    if Context.verbose:
        print("\nUser prompt:", user_prompt)
        print("\nSystem prompt:", system_prompt)
        print_chat(chat_history)

    full_response = generate_response_from_openai(model, system_prompt, user_prompt, chat_history)

    if Context.verbose:
        print("\n\nFull response:\n", full_response)

    # Search for the code pattern in the text
    import re
    pattern = re.compile(r'([\s\S]*?)```python([\s\S]*?)```')
    match = pattern.search(full_response)
    if match:
        text = match.group(1).strip()
        code = match.group(2).strip()
    else:
        text = full_response
        code = None


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
    The code will be executed by the user within a Jupyter notebook.
    You can only use these python libraries: {",".join([str(v) for v in libraries])}.
    If you create images, show them using matplotlib and save them in variables for later reuse.
    The following variables are available: {",".join([str(v) for v in variables])}
    Do not set the values of the variables that are available.
    The following functions are available: {",".join([str(v) for v in functions])}
    
    Before writing the code, provide a concise step-by-step plan 
    of what the code will be going to do. 
    This plan must not contain any "`" characters and should be written in plain text.
    Then print the code.
    Importantly, the code block must start with the line: 
    ```python
    and it must end with the line:
    ```
    There must be no text after the code block.
    If the request does not require to write code, simply answer in plain text.
    """
    return system_prompt


def print_chat(chat):
    print("\nChat history:")
    for message in chat:
        role = message['role']
        content = message['content']
        print(role)
        print(content)


def concatenate_chat_content(chat):
    concatenated_chat = ""
    for message in chat:
        concatenated_chat += message['content']
    return concatenated_chat


def output_text(text):
    """Display markdown content in the notebook."""
    from IPython.display import display, Markdown
    display(Markdown(text))


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

    return reply


def available_models():
    import openai
    models = openai.Model.list()
    for model in models['data']:
        print(model['id'])
