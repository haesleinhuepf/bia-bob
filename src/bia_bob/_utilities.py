def generate_response_to_user(model, user_prompt: str, image=None, additional_system_prompt: str = None, max_number_attempts:int = 3):
    """Generates code and text respond for a specific user input.
    To do so, it combines the user input with additional context such as
    current variables and a prompt template."""
    from ._machinery import Context

    text, plan, code = None, None, None

    chat_backup = [c for c in Context.chat]

    for attempt in range(1, max_number_attempts + 1):
        system_prompt = create_system_prompt()
        if additional_system_prompt is not None:
            system_prompt += "\n" + additional_system_prompt

        # take the last n chat entries
        n = 10
        chat_history = Context.chat[-n:]

        if Context.verbose:
            print("\nUser prompt:", user_prompt)
            print("\nSystem prompt:", system_prompt)
            print_chat(chat_history)

        if "gpt-" in model:
            full_response = generate_response_from_openai(model, system_prompt, user_prompt, chat_history, image)
        elif "gemini-" in model:
            full_response = generate_response_from_vertex_ai(model, system_prompt, user_prompt, chat_history, image)
        else:
            raise RuntimeError(f"Unknown model API for {model}")

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

        # split response in text and code
        text, plan, code = split_response(full_response)

        if text is not None and plan is not None:
            break

        print(f"There was an issue. Retrying ({attempt}/{max_number_attempts})...")
        Context.chat = chat_backup

    return code, text

def split_response(text):
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

    if code is not None:
        parts = code.split("```")
        if len(parts) == 1:
            code = None
        else:
            text = ""
            code = ""
            for t, c in zip(parts[::2], parts[1::2]):
                code = code + c
            code = code.strip("\n")

    return summary, plan, code


def create_system_prompt(reusable_variables_block=None):
    """Creates a system prompt that contains instructions of general interest, available functions and variables."""
    # determine useful variables and functions in context

    # if scikit-image is installed, give hints how to use it
    from ._machinery import Context

    skimage_snippets = """
    * Load an image file from disc and store it in a variable:
    ```
    from skimage.io import imread
    image = imread(filename)
    ```
    * Expanding labels by a given radius in a label image works like this:
    ```
    from skimage.segmentation import expand_labels
    expanded_labels = expand_labels(label_image, distance=10)
    ```
    * Measure properties of labels with respect to an image works like this:
    ```
    from skimage.measure import regionprops
    properties = regionprops(label_image, image)
    ```
    """
    if "scikit-image" not in Context.libraries:
        skimage_snippets = ""

    # if aicsimageio is installed, give hints how to use it
    aicsimageio_snippets = """
    * Loading files with endings other than `.tif`, `.png` or `.jpg` works like this:
    ```
    from aicsimageio import AICSImage
    aics_image = AICSImage(image_filename)
    image = aics_image.get_image_data("ZYX")
    ```
    """
    if "aicsimageio" not in Context.libraries:
        aicsimageio_snippets = ""

    if reusable_variables_block is None:
        reusable_variables_block = create_reusable_variables_block()

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
            func = ep.load()

            # load instructions from a plugin
            instructions = func()
            # special treatment for code snippets from stackview, as it won't work with the custom kernel
            if "stackview" not in instructions or "stackview" in Context.libraries:
                additional_instructions.append(instructions)

        additional_snippets = "\n".join(additional_instructions)
    else:
        additional_snippets = ""

    system_prompt = f"""
    You are a extremely talented bioimage analyst and you use Python to solve your tasks unless stated otherwise.
    If the request entails writing code, write concise professional bioimage analysis high-quality code.
    If there are several ways to solve the task, chose the option with the least amount of code.    
    If there is no specific programming language required, write python code and follow the below instructions.
    
    {reusable_variables_block}
    
    ## Python specific code snippets
    
    If the user asks for those simple tasks, use these code snippets.
    {skimage_snippets}
    {aicsimageio_snippets}
    {additional_snippets}
    
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


def create_reusable_variables_block():
    """Creates a block of text that explains which variables, functions and libraries are
    available to be used."""
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

    return f"""
    ## Python specific instructions
    
    For python, you can only use those libraries: {",".join([str(v) for v in libraries])}.
    If you create images, show the results and save them in variables for later reuse.
    The following variables are available: {",".join([str(v) for v in variables])}
    NEVER the values of the variables that are available.
    
    The following functions are available: {",".join([str(v) for v in functions])}
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

    if Context.seed is not None:
        kwargs['seed'] = Context.seed
    if Context.temperature is not None:
        kwargs['temperature'] = Context.temperature

    # init client
    if Context.client is None or not isinstance(Context.client, OpenAI):
        Context.client = OpenAI()

    # retrieve answer
    response = Context.client.chat.completions.create(
        messages=system_message + chat_history + image_message + user_message,
        model=model,
        **kwargs
    )  # stream=True would be nice
    reply = response.choices[0].message.content

    # store question and answer in chat history
    assistant_message = [{"role": "assistant", "content": reply}]
    Context.chat += user_message + assistant_message

    return reply


def generate_response_from_vertex_ai(model: str, system_prompt: str, user_prompt: str, chat_history, image=None):
    """A prompt helper function that sends a message to Google Vertex AI
    and returns only the text response.

    See also
    --------
    https://colab.research.google.com/github/GoogleCloudPlatform/generative-ai/blob/main/gemini/getting-started/intro_gemini_python.ipynb#scrollTo=SFbGVflTfBBk
    """
    # from vertexai.generative_models._generative_models import ChatSession
    from ._machinery import Context
    from vertexai.preview.generative_models import (
        GenerationConfig,
        GenerativeModel,
        Image,
        Part,
        ChatSession,
    )


    if "vision" in Context.model:
        # We need to do some special case here, because the vision model seems to not support chats (yet).
        if Context.client is None or not isinstance(Context.client, GenerativeModel):
            Context.client = GenerativeModel(Context.model)

        if image is None:
            prompt = f"""
                       {system_prompt}
                       
                       # Task
                       This is the task:
                       {user_prompt}
                       
                       Remember: Your output should be 1) a summary, 2) a plan and 3) the code.
                       """
        if image is not None:
            from stackview._image_widget import _img_to_rgb
            from darth_d._utilities import numpy_to_bytestream

            rgb_image = _img_to_rgb(image)
            byte_stream = numpy_to_bytestream(rgb_image)

            image = Image.from_bytes(byte_stream)

            prompt = f"""
                   {system_prompt}

                   # Task
                   This is the task:
                   {user_prompt}

                   If the task is not explicitly about generating code, do not generate any code.
                   """

            prompt = [image, prompt]

        response = Context.client.generate_content(prompt).text

    else:

        system_prompt = create_system_prompt(reusable_variables_block="")

        if Context.client is None or not isinstance(Context.client, ChatSession):
            model = GenerativeModel(Context.model)
            Context.client = model.start_chat()
            system_result = Context.client.send_message(system_prompt + "\n\nConfirm these general instructioons by answering 'yes'.").text

        reusable_variables_block = create_reusable_variables_block()

        prompt = f"""{reusable_variables_block}
        
        # Task
        This is the task:
        {user_prompt}
        
        Remember: Your output should be 1) a step-by-step plan and 2) code.
        """

        response = Context.client.send_message(prompt).text

    return response


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
    """Returns a list of available model names"""
    models = []
    try:
        from openai import OpenAI
        client = OpenAI()
        models = models + [model.id for model in client.models.list().data]
    except:
        print("Error while adding OpenAI models")
        pass

    try:
        from vertexai.preview.generative_models import GenerativeModel
        models.append("gemini-pro")
        models.append("gemini-pro-vision")
    except:
        print("Error while adding VertexAI models")
        pass

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

