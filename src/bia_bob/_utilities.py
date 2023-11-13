def generate_response_to_user(model, user_prompt: str, image=None):
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

    full_response = generate_response_from_openai(model, system_prompt, user_prompt, chat_history, image)

    if Context.verbose:
        print("\n\nFull response:\n", full_response)

    full_response = full_response\
                    .replace("```python", "```")\
                    .replace("```nextflow", "```")\
                    .replace("```java", "```")\
                    .replace("```javascript", "```")\
                    .replace("```macro", "```")\
                    .replace("```groovy", "```")\
                    .replace("```jython", "```")

    # Search for the code pattern in the text
    import re
    pattern = re.compile(r'([\s\S]*?)```([\s\S]*?)```')
    match = pattern.search(full_response)
    if match:
        text = match.group(1).strip()
        code = match.group(2).strip()
    else:
        text = full_response
        code = None


    return code, text


def create_system_prompt():
    """Creates a system prompt that contains instructions of general interest, available functions and variables."""
    # determine useful variables and functions in context
    variables = []
    functions = []
    from ._machinery import Context

    # figure out which variables are not private
    for key, value in Context.variables.items():
        if key.startswith("_"):
            continue
        if callable(value):
            if key not in ["quit", "exit"]:
                functions.append(key)
            continue
        variables.append(key)

    libraries = Context.libraries

    system_prompt = f"""
    If the request entails writing code, write concise professional bioimage analysis high-quality code.
    If there are several ways to solve the task, chose the option with the least amount of code.
    
    If there is no specific programming language required, write python code and follow the below instructions.
    
    ## Python specific instruction
    
    For python, you can only use those libraries: {",".join([str(v) for v in libraries])}.
    If you create images, show the results and save them in variables for later reuse.
    The following variables are available: {",".join([str(v) for v in variables])}
    Do not set the values of the variables that are available.
    The following functions are available: {",".join([str(v) for v in functions])}
    
    ### Python specific code snippets
    
    If the user asks for those simple tasks, use these code snippets.
    * Load a image file from disc and store it in a variable:
    ```
    from skimage.io import imread
    image = imread(filename)
    ```
    * Display an image stored in a variable `image` (this also works with label images):
    ```
    import stackview
    stackview.insight(image)
    ```
    * Slicing an image stored in a variable `image`:
    ```
    import stackview
    stackview.slice(image)
    ```
    * Showing an image stored in variable `image` and a segmented image stored in variable `labels` on top:
    ```
    import stackview
    stackview.curtain(image, labels)
    ```
    * Expanding labels by a given radius in a label image works like this:
    ```
    from skimage.segmentation import expand_labels
    expanded_labels = expand_labels(label_image, radius=10)
    ```
    
    ## Explanations and code
    
    Before writing any code, provide a concise step-by-step plan 
    of what the code will be going to do. Always provide the plan first.
    This plan must not contain any "`" characters, no code examples, and should be written in plain text.
    
    After the plan, print the code.
    There must be only one code block.
    Importantly, the code block must start with the line: 
    ```
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


def generate_response_from_openai(model: str, system_prompt: str, user_prompt: str, chat_history, image=None):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    """
    from openai import OpenAI
    from ._machinery import Context

    # assemble prompt
    system_message = [{"role": "system", "content": system_prompt}]
    user_message = [{"role": "user", "content": user_prompt}]
    image_message = []
    kwargs = {}

    if image is not None:
        image_message = image_to_message(image)

    if model == "gpt-4-vision-preview":
        # this seems necessary according to the docs:
        # https://platform.openai.com/docs/guides/vision
        # if it is not provided, the response will be
        # cropped to half a sentence
        kwargs['max_tokens'] = 3000

    # init client
    client = OpenAI()

    # retrieve answer
    response = client.chat.completions.create(
        messages=system_message + chat_history + image_message + user_message,
        model=model,
        **kwargs
    )  # stream=True would be nice
    reply = response.choices[0].message.content

    # store question and answer in chat history
    assistant_message = [{"role": "assistant", "content": reply}]
    Context.chat += user_message + assistant_message

    return reply


def image_to_message(image):
    import base64

    from stackview._image_widget import _img_to_rgb
    from darth_d._utilities import numpy_to_bytestream

    rgb_image = _img_to_rgb(image)
    byte_stream = numpy_to_bytestream(rgb_image)
    base64_image = base64.b64encode(byte_stream).decode('utf-8')

    return [{"role": "user", "content": [{
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_image}",
    }]}]


def is_image(potential_image):
    """Returns true if the given object is a numpy-compatible image/array."""
    return hasattr(potential_image, "shape") and hasattr(potential_image, "dtype")


def available_models():
    """Returns a list of available model names in openAI."""
    from openai import OpenAI
    client = OpenAI()
    models = client.models.list()
    return sorted([model.id for model in models.data])


def keep_available_packages(libraries):
    """Goes through a given list of package names and return those that are installed on the system."""
    try:
        # Python 3.8+
        from importlib.metadata import distributions
    except ImportError:
        # Python < 3.8
        from importlib_metadata import distributions

    installed = [dist.metadata['Name'] for dist in distributions()]
    result = [i for i in libraries if i in installed]

    return result

