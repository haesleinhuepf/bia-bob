def generate_response_from_mistral(model: str, system_prompt: str, user_prompt: str, chat_history, image = None,
base_url:str = None, api_key:str = None, vision_model:str = None, vision_system_prompt:str = None):
    from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
    from .._machinery import Context
    import warnings

    if image is not None:
        warnings.warn("Images are not supported for mistral models and will be ignored.")

    if Context.client is None or not isinstance(Context.client, Mistral):
        Context.client = Mistral(api_key=api_key, server_url=base_url)
    client = Context.client

    system_message = SystemMessage(content=system_prompt)
    user_message = UserMessage(content=user_prompt)

    messages = [system_message]
    for m in chat_history:
        messages.append(m)
    messages.append(user_message)

    response = client.chat.complete(
        model=model,
        messages=messages,
        temperature=1.0,
        max_tokens=4096,
        top_p=1.0
    ).choices[0].message.content

    chat_history.append(UserMessage(content=user_prompt))
    chat_history.append(AssistantMessage(content=response))

    return response