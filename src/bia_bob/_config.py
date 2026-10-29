def config_ollama(model="flint:latest", vision_model="flint:latest", fast_model="flint:latest"):
    from bia_bob._machinery import Context
    Context.model = model
    Context.vision_model = vision_model
    Context.fast_model = fast_model
    Context.endpoint = "http://localhost:11434/v1"
    Context.api_key = "ollama" # this is ignored
    Context.refine_code = False
    Context.disclaimer_shown = False

def config_blablador(model="alias-code", vision_model="alias-code", fast_model="alias-fast"):
    """
    To use the LLM-infrastructure provided by FZ Jülich via this configuration, 
    you need to acquire an API KEY as explained here: 
    https://sdlaml.pages.jsc.fz-juelich.de/ai/guides/blablador_api_access/#step-2-obtain-an-api-key 
    
    It is recommended to store this key as environment variable "BLABLADOR_API_KEY".
    """
    import os
    from getpass import getpass

    from bia_bob._machinery import Context
    Context.model = model
    Context.vision_model = vision_model
    Context.fast_model = fast_model
    Context.endpoint = "https://api.blablador.fz-juelich.de/v1/"

    api_key = os.getenv("BLABLADOR_API_KEY")
    if api_key is None:
        print("BLABLADOR_API_KEY environment variable not found. If you don't have it yet, get one as explained on this page: https://sdlaml.pages.jsc.fz-juelich.de/ai/guides/blablador_api_access/")
        api_key = getpass("Please enter your BLABLADOR_API_KEY:")

    Context.api_key = api_key
    Context.refine_code = False
    Context.disclaimer_shown = False

def config_scadsai(model="alias-code", vision_model="alias-vision", fast_model="alias-code"):
    """
    To use the LLM-infrastructure provided by ZIH TU Dresden via this configuration, 
    you need to acquire an API KEY as explained here:
    https://llm.scads.ai/docs/usage/api/
    
    It is recommended to store this key as environment variable "SCADSAI_API_KEY".
    """
    import os
    from getpass import getpass

    from bia_bob._machinery import Context
    Context.model = model
    Context.vision_model = vision_model
    Context.fast_model = fast_model
    Context.endpoint = "https://llm.scads.ai/v1"

    api_key = os.getenv("SCADSAI_API_KEY3")
    if api_key is None:
        print("SCADSAI_API_KEY environment variable not found. If you don't have it yet, get one as explained on this page: https://llm.scads.ai/docs/usage/api/")
        api_key = getpass("Please enter your SCADSAI_API_KEY:")

    Context.api_key = api_key
    Context.refine_code = False
    Context.disclaimer_shown = False
