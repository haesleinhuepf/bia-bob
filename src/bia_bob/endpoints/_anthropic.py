def generate_response_from_anthropic(model: str, system_prompt: str, user_prompt: str, chat_history, image=None,
                                  base_url:str=None, api_key:str=None, vision_model:str = None, vision_system_prompt:str = None):
    # e.g. claude-3-5-sonnet-20240620 or claude-3-opus-20240229
    from anthropic import Anthropic
    from .._machinery import Context

    if image is None:
        if Context.client is None or not isinstance(Context.client, Anthropic):
            Context.client = Anthropic(base_url=base_url, api_key=api_key)
        system_message = system_prompt
        user_message = [{
                    "role": "user",
                    "content": user_prompt,
                }]
        client = Context.client
    else:
        if Context.vision_client is None or not isinstance(Context.vision_client, Anthropic):
            Context.vision_client = Anthropic(base_url=base_url, api_key=api_key)
        system_message = vision_system_prompt
        user_message = image_to_message_claude(image, user_prompt)
        client = Context.vision_client
        model = vision_model

    messages = [c for c in chat_history]
    messages.append(user_message[0])


    if Context.verbose:
        for i, m in enumerate(messages):
            print(f"\n\nMESSAGE {i}: {m}")

    response = client.messages.create(
        messages=messages,
        system=system_message,
        model=model,
        max_tokens=4096,
    )
    reply = response.content[0].text

    assistant_message = [{"role": "assistant", "content": reply}]

    #Context.chat += user_message + assistant_message
    if image is None:
        chat_history.append(user_message[0])
        chat_history.append(assistant_message[0])

    return reply


def image_to_message_claude(image, prompt):
    import base64
    from .._utilities import numpy_to_bytestream

    from stackview._image_widget import _img_to_rgb

    rgb_image = _img_to_rgb(image)
    byte_stream = numpy_to_bytestream(rgb_image)
    base64_image = base64.b64encode(byte_stream).decode('utf-8')

    return [{
            "role": 'user',
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_image}},
                {"type": "text", "text": prompt}
            ]
        }]
