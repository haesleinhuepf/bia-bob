from IPython.core.magic import register_line_cell_magic


def acc(line:str=None, cell:str=None):
    """
    This Jupyter Magic automatically accelerates code by replacing functions from libraries with CUDA/OpenCL-
    accelerated functions.
    """
    from ._machinery import Context, init_assistant, combine_user_input
    from ._utilities import generate_response_to_user
    from IPython.core.getipython import get_ipython

    candidates = ["pyclesperanto", "pyclesperanto_prototype", "cupy", "cudf", "dask_image"]
    packages = ",".join([p for p in Context.libraries if p in candidates])

    code = combine_user_input(line, cell)

    prompt = f"""
    Analyze the following code and try to find scikit-image, scipy, numpy, cv2 or pandas functions that can be 
    replaced by corresponding functions from the {packages} libraries. List those functions in plain text.
    Rewrite the code using the functions from {packages}. 
    Make sure that the code still does the same as before. 
    
    ```python
{code}
    ```
    """

    if Context.model is None:
        init_assistant()
    p = get_ipython()

    code, text = generate_response_to_user(Context.model, prompt)

    p.set_next_input(code, replace=True)


try:
    register_line_cell_magic(acc)
except NameError:
    pass

