def make_variable_name(name: str) -> str:
    name = name.replace(".", "_")
    name = name.replace("/", "_")
    name = name.replace("\\", "_")
    name = name.replace(" ", "_")

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


def find_image(variables, key):
    from ._machinery import _context
    if key in variables.keys():
        return variables[key]

    other_name = make_variable_name(key)
    if other_name in variables.keys():
        return variables[other_name]

    other_name = find_best_fit(variables.keys(), key)
    if _context.verbose:
        print("Searching for variable named ", other_name)
    return variables[other_name]