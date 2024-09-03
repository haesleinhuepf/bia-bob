
def generate_response_from_vertex_ai(model: str, system_prompt: str, user_prompt: str, chat_history, image=None,
                                     vision_model: str = None, vision_system_prompt: str = None):
    """A prompt helper function that sends a message to Google Vertex AI
    and returns only the text response.

    See also
    --------
    https://colab.research.google.com/github/GoogleCloudPlatform/generative-ai/blob/main/gemini/getting-started/intro_gemini_python.ipynb#scrollTo=SFbGVflTfBBk
    """
    # from vertexai.generative_models._generative_models import ChatSession
    from .._machinery import Context
    from .._utilities import numpy_to_bytestream, create_system_prompt
    from vertexai.preview.generative_models import (
        GenerationConfig,
        GenerativeModel,
        Image,
        Part,
        ChatSession,
    )

    # if "vision" in Context.model:
    # We need to do some special case here, because the vision model seems to not support chats (yet).

    if image is None:
        if Context.client is None or not isinstance(Context.client, ChatSession):
            gemini_model = GenerativeModel(model)
            Context.client = gemini_model.start_chat()
            system_result = Context.client.send_message(
                system_prompt + "\n\nConfirm these general instructions by answering 'yes'.").text

        if len(system_prompt) > 0:
            system_prompt = create_system_prompt(reusable_variables_block="")

        prompt = f"""
                   {system_prompt}

                   # Task
                   This is the task:
                   {user_prompt}

                   Remember: Your output should be 1) a summary, 2) a plan and 3) the code.
                   """

        response = Context.client.send_message(prompt).text

    else:  # if image is not None:
        if Context.client is None or not isinstance(Context.client, GenerativeModel):
            Context.vision_client = GenerativeModel(vision_model)

        from stackview._image_widget import _img_to_rgb

        rgb_image = _img_to_rgb(image)
        byte_stream = numpy_to_bytestream(rgb_image)

        image = Image.from_bytes(byte_stream)

        prompt = f"""
               {vision_system_prompt}

               # Task
               This is the task:
               {user_prompt}
               """

        prompt = [image, prompt]

        response = Context.vision_client.generate_content(prompt).text

    return response


def generate_response_from_google_ai(model: str, system_prompt: str, user_prompt: str, chat_history, image=None,
                                     vision_model: str = None, vision_system_prompt: str = None):
    """A prompt helper function that sends a message to Google AI
    and returns only the text response.
    """
    from .._machinery import Context
    from .._utilities import create_system_prompt
    from google import generativeai as genai

    if image is None:
        if Context.client is None or not isinstance(Context.client, genai.ChatSession):
            Context.client = genai.GenerativeModel(model)

        if len(system_prompt) > 0:
            system_prompt = [{"role": "system", "content": create_system_prompt() +
                              "\n\nConfirm these general instructions by answering 'ok'."},
                             {"role": "user", "content": "ok"}]
        else:
            system_prompt = []

        prompt = [{"role": "user", "content":user_prompt}]

        messages = system_prompt
        for m in chat_history:
            messages.append(m)
        messages.append(prompt[0])

        response = Context.client.generate_content(messages_to_google_messages(messages)).candidates[0].content.parts[
            0].text

    else:  # if image is not None:
        if Context.vision_client is None or not isinstance(Context.vision_client, genai.GenerativeModel):
            Context.vision_client = genai.GenerativeModel(vision_model)

        import numpy as np
        from PIL import Image
        pil_image = Image.fromarray(np.uint8(image))

        if len(system_prompt) > 0:
            system_prompt = [{"role": "user", "content": vision_system_prompt +
                              "\n\nConfirm these general instructions by answering 'ok'."},
                             {"role": "assistant", "content": "ok"}]
        else:
            system_prompt = []

        prompt = [{"role": "user", "content": [pil_image, user_prompt]}]

        messages = system_prompt
        for m in chat_history:
            messages.append(m)
        messages.append(prompt[0])

        response = Context.vision_client.generate_content(messages_to_google_messages(messages)).candidates[0].content.parts[
            0].text

    chat_history.append({
        "role": "user",
        "content": user_prompt
    })
    chat_history.append({
        "role": "assistant",
        "content": response
    })

    return response


def messages_to_google_messages(messages):
    result = []
    for message in messages:
        role = message["role"]
        if role != "user":
            role = "model"
        content = message["content"]

        if type(content) == str:
            result.append({"role": role,
                           "parts": [{
                               "text": content
                           }]
                           })
        elif type(content) == list:
            parts = []
            for part in content:
                if type(part) == str:
                    parts.append({
                               "text": part
                           })
                else:
                    parts.append({
                        "inline_data": part
                    })
            result.append({"role": role,
                           "parts": parts
                           })
        else:
            result.append({"role": role,
                               "parts": [{
                                   "inline_data": content
                               }]
                           })
    return result