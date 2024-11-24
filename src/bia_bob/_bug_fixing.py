from IPython.core.magic import register_line_cell_magic


def fix(line: str = None, cell: str = None):
    """This Jupyter Magic automatically fixes code when it's in the first line of a cell that caused an error that just
    happened.
    """
    from IPython.core.getipython import get_ipython
    from ._machinery import bob, combine_user_input, Context, init_assistant
    from ._utilities import generate_response_to_user

    ip = get_ipython()
    if cell is None and line is None:
        # if the function was called as fix(), it will use the last executed cell instead of the magic-marked cell
        variables = get_ipython().user_ns
        code = variables['_i']
    else:
        code = combine_user_input(line, cell)

    # this reads the last error that occurred
    error = ip.get_exception_only()

    prompt = f"""
I executed this code:
```python
{code}
```

And this error occurred:
```
{error}
```

Please correct the code. Return the entire code block, not just the correction.
"""

    if Context.model is None:
        init_assistant()
    p = get_ipython()

    code, text = generate_response_to_user(Context.model, prompt)

    p.set_next_input(code, replace=True)


try:
    register_line_cell_magic(fix)
except NameError:
    pass


