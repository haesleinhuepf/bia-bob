def make_variable_name(name: str) -> str:
    name = name.replace(".", "_")
    name = name.replace("/", "_")
    name = name.replace("\\", "_")
    name = name.replace(" ", "_")

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
    from ._machinery import _context
    if key in variables.keys():
        return variables[key]

    other_name = make_variable_name(key)
    if other_name in variables.keys():
        return variables[other_name]

    other_name = find_best_fit([v for v in variables.keys() if is_image(variables[v])], key)
    if _context.verbose:
        print("Searching for variable named ", other_name)
    return variables[other_name]

def generate_code(task):
    code = prompt(task)

    code = code.replace("```python", "```")
    code = code.replace("```", "")

    return code

def prompt(message:str, model="gpt-3.5-turbo"):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    """
    import openai

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": message}]
    )
    return response['choices'][0]['message']['content']

