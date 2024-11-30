def generate_response_from_mistral(model: str, system_prompt: str, user_prompt: str, chat_history, image = None,
base_url:str = None, api_key:str = None, vision_model:str = None, vision_system_prompt:str = None):
    from mistralai import Mistral, UserMessage, SystemMessage, AssistantMessage
    from .._machinery import Context
    import os

    if api_key is None:
        api_key = os.getenv("MISTRAL_API_KEY")

    if Context.client is None or not isinstance(Context.client, Mistral):
        Context.client = Mistral(api_key=api_key, server_url=base_url)
    client = Context.client

    if image is None:
        system_message = {
                "role": "system",
                "content": system_prompt
        }
        user_message = {
                "role": "user",
                "content": user_prompt
            }

    else:
        system_message = {
            "role": "system",
            "content": vision_system_prompt
        }
        user_message = image_to_message_mistral(image, user_prompt)[0]

    messages = [system_message]
    for m in chat_history:
        messages.append(m)
    messages.append(user_message)

    if image is not None:
        model = vision_model

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



def image_to_message_mistral(image, prompt):
    import base64
    from .._utilities import numpy_to_bytestream

    from stackview._image_widget import _img_to_rgb

    rgb_image = _img_to_rgb(image)
    byte_stream = numpy_to_bytestream(rgb_image)
    base64_image = base64.b64encode(byte_stream).decode('utf-8')

    return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/png;base64,{base64_image}"
                    }
                ]
            }
        ]