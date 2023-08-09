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