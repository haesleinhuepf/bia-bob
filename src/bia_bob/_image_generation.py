from IPython.core.magic import register_line_cell_magic

def alice(line: str = None, cell: str = None):
    """
    Juptyer magic to generate an image from a given prompt.
    The image is stored in the Context (e.g. global variables). In case behind %%alice comes just a single word, the
    image variable will be named like this. Otherwise `ìmage_1` or similar will be used.
    """
    from ._machinery import Context, combine_user_input, init_assistant
    from ._utilities import output_text
    import stackview

    if Context.model is None:
        init_assistant()

    potential_variable_name = line.strip()
    if ' ' in potential_variable_name:
        for i in range(1, 100):
            if f'image_{i}' not in Context.variables:
                potential_variable_name = f'image_{i}'
                break
        user_input = combine_user_input(line, cell)
    else:
        user_input = cell

    image = generate_image_from_openai(user_input)

    stackview.imshow(image)

    Context.variables[potential_variable_name] = stackview._static_view.StackViewNDArray(image)
    output_text(f"Generated image is stored as `{potential_variable_name}`.")

try:
    register_line_cell_magic(alice)
except NameError:
    pass

def generate_image_from_openai(message: str, width:int=1024, height:int=1024):
    """
    Generate an image from a given prompt.
    """
    from ._machinery import Context
    from openai import OpenAI
    from skimage.io import imread

    client = OpenAI()
    response = client.images.generate(
        model=Context.imagen_model,
        prompt=message,
        n=1,
        size=f"{width}x{height}"
    )
    image_url = response.data[0].url
    return imread(image_url)