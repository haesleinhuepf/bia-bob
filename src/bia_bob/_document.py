
from IPython.core.magic import register_cell_magic
@register_cell_magic
def document(line:str, cell:str):
    """
    This Jupyter Magic automatically documents code when its in the first line of a cell.

    Usage:
    ```
    import bia_bob
    ```
    ```
    %%document
    ... code you would like do document better
    ```
    """
    from ._machinery import Context, init_assistant
    from ._utilities import generate_response_to_user
    from IPython.core.getipython import get_ipython

    prompt = f"""
    Please add numpy-style docstrings and comments to this code:
    ```python
    {cell}
    ```
    """

    if Context.assistant is None:
        init_assistant()
    p = get_ipython()
    Context.variables = p.user_ns

    code, text = generate_response_to_user(Context.assistant.model, prompt)

    p.set_next_input(code, replace=True)


