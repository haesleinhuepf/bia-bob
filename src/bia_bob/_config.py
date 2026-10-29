def config_ollama(model="flint:latest", vision_model="flint:latest", fast_model="flint:latest"):
    from bia_bob._machinery import Context
    Context.model = model
    Context.vision_model = vision_model
    Context.fast_model = fast_model
    Context.endpoint = "http://localhost:11434/v1"
    Context.api_key = "ollama" # this is ignored
    Context.refine_code = False

