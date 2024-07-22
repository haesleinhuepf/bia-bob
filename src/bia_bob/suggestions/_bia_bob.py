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
    
    You can also submit a prompt without system prompts to the LLM and retrieve the response as string like this:
    (Note that the image parameter is optional)
    ```python
    from bia_bob import ask_llm
    code = ask_llm("Do this, that and by the end, show the result.", image=image)
    exec(code)
    ```
    """