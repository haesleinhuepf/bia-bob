def suggestions():
    return """
    ### Prompt-engineering for scientific image/data analysis using bia-bob
    
    When writing prompts, instead of Python code, you can use the following syntax:
    ```python
    %%bob
    * Do this, 
    * that and 
    * by the end, show the result.
    ```
    
    If you explicitly wish to do this with Python code, you can do it like this:
    
    ```python
    from bia_bob import bob
    code = bob("Do this, that and by the end, show the result.")
    exec(code)
    ```
    """