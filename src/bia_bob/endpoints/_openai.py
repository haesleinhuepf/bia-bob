def generate_response_from_openai(model: str, system_prompt: str, user_prompt: str, chat_history, image=None,
                                  base_url:str=None, api_key:str=None, vision_model:str = None, vision_system_prompt:str = None):
    """A prompt helper function that sends a message to openAI
    and returns only the text response.
    """
    from openai import OpenAI
    from .._machinery import Context

    # assemble prompt
    user_message = [{"role": "user", "content": user_prompt}]
    image_message = []
    kwargs = {}
    model_init_kwargs = {}

    if api_key is not None:
        model_init_kwargs['api_key'] = api_key
    if base_url is not None:
        model_init_kwargs['base_url'] = base_url

    if image is None: # normal text-based prompt
        system_message = [{"role": "system", "content": system_prompt}]

        # init client
        if Context.client is None or not isinstance(Context.client, OpenAI):
            Context.client = OpenAI(**model_init_kwargs)
        client = Context.client
    else:
        system_message = [{"role": "system", "content": vision_system_prompt}]
        image_message = image_to_message(image)

        if vision_model == 'gpt-4-vision-preview':
            # this seems necessary according to the docs:
            # https://platform.openai.com/docs/guides/vision
            # if it is not provided, the response will be
            # cropped to half a sentence
            kwargs['max_tokens'] = 3000

        if Context.vision_client is None or not isinstance(Context.vision_client, OpenAI):
            Context.vision_client = OpenAI(**model_init_kwargs)
        client = Context.vision_client
        model = vision_model

    if Context.seed is not None:
        kwargs['seed'] = Context.seed
    if Context.temperature is not None:
        kwargs['temperature'] = Context.temperature

    # retrieve answer
    messages = system_message
    for m in chat_history:
        messages.append(m)
    for m in image_message:
        messages.append(m)
    messages.append(user_message[0])

    if Context.verbose:
        for i, m in enumerate(messages):
            print(f"\n\nMESSAGE {i}: {m}")

    response = client.chat.completions.create(
        messages=messages,
        model=model,
        **kwargs
    )  # stream=True would be nice
    reply = response.choices[0].message.content

    # store question and answer in chat history
    assistant_message = [{"role": "assistant", "content": reply}]

    #Context.chat += user_message + assistant_message
    chat_history.append(user_message[0])
    chat_history.append(assistant_message[0])

    return reply


def image_to_message(image):
    from .._utilities import image_to_url


    return [{"role": "user", "content": [{
        "type": "image_url",
        #"image_url": f"data:image/jpeg;base64,{base64_image}",
        # from: https://platform.openai.com/docs/guides/vision
        "image_url": {
            "url": image_to_url(image)
        }

    }]}]



def image_to_message_llava(image, prompt):
    import base64

    from stackview._image_widget import _img_to_rgb
    from .._utilities import numpy_to_bytestream

    rgb_image = _img_to_rgb(image)
    byte_stream = numpy_to_bytestream(rgb_image)
    base64_image = base64.b64encode(byte_stream).decode('utf-8')

    return [{
        'role': 'user',
        'content': prompt,
        'images': [base64_image]
    }]
