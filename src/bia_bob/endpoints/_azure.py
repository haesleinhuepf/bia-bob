def generate_response_from_azure(model: str, system_prompt: str, user_prompt: str, chat_history, image = None,
base_url:str = None, api_key:str = None, vision_model:str = None, vision_system_prompt:str = None):
    from .._machinery import Context
    from .._utilities import image_to_url
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        SystemMessage,
        UserMessage,
        TextContentItem,
        ImageContentItem,
        ImageUrl,
        ImageDetailLevel,
        AssistantMessage
    )
    from azure.core.credentials import AzureKeyCredential

    if image is None:
        system_message = SystemMessage(content=system_prompt)
        user_message = UserMessage(content=user_prompt),
        if Context.client is None or not isinstance(Context.client, ChatCompletionsClient):
            Context.client = ChatCompletionsClient(
                endpoint=base_url,
                credential=AzureKeyCredential(api_key),
            )
        client = Context.client
    else:
        system_message = SystemMessage(content=vision_system_prompt)
        user_message = UserMessage(content=[
                TextContentItem(text=user_prompt),
                ImageContentItem(
                    image_url=image_to_url(image)
                ),
            ],
        )
        if Context.vision_client is None or not isinstance(Context.vision_client, ChatCompletionsClient):
            Context.vision_client = Context.client = ChatCompletionsClient(
                endpoint=base_url,
                credential=AzureKeyCredential(api_key),
            )
        client = Context.vision_client
        model = vision_model

    messages = [system_message]
    for m in chat_history:
        messages.append(m)
    messages.append(user_message)

    response = client.complete(
        messages=messages,
        temperature=1.0,
        top_p=1.0,
        max_tokens=4096,
        model=model
    ).choices[0].message.content

    chat_history.append(UserMessage(content=user_prompt))
    chat_history.append(AssistantMessage(content=response))

    return response