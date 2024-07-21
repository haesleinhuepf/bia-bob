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

    # if "vision" in Context.model:
    # We need to do some special case here, because the vision model seems to not support chats (yet).

    if image is None:
        print("using googleai", user_prompt)

        if Context.client is None or not isinstance(Context.client, genai.ChatSession):
            Context.client = genai.GenerativeModel(model)
            # gemini_model = genai.GenerativeModel(model)
            # print("Starting chat")
            # Context.client = gemini_model.start_chat()
            # if system_prompt is not None and len(system_prompt) > 0:
            #    Context.client.send_message(system_prompt)

        if len(system_prompt) > 0:
            system_prompt = [{"role": "system", "content": create_system_prompt(reusable_variables_block="") +
                              "\n\nConfirm these general instructions by answering 'ok'."},
                             {"role": "user", "content": "ok"}]
        else:
            system_prompt = []

        prompt = [{"role": "user", "content": f"""# Task
                   This is the task:
                   {user_prompt}
                   Remember: Your output should be 1) a summary, 2) a plan and 3) the code.
                   """}]

        print("submitting", type(prompt))

        response = Context.client.generate_content(messages_to_google_messages(chat_history + system_prompt + prompt)).candidates[0].content.parts[
            0].text
        # response = Context.client.send_message(prompt).candidates[0].content.parts[0].text
        print("response:", response)

    else:  # if image is not None:
        print("using googleai vision", user_prompt)

        if Context.vision_client is None or not isinstance(Context.vision_client, genai.GenerativeModel):
            Context.vision_client = genai.GenerativeModel(vision_model)

        import numpy as np
        from PIL import Image
        pil_image = Image.fromarray(np.uint8(image))

        prompt = f"""
               {vision_system_prompt}


               # Task
               This is the task:
               {user_prompt}
               """

        prompt = [pil_image, prompt]



        response = Context.vision_client.generate_content(messages_to_google_messages(Context.chat_history + prompt)).candidates[0].content.parts[
            0].text

        print("Response was:", response)

    return response


def messages_to_google_messages(messages):
    result = []
    for message in messages:
        role = message["role"]
        print("role", role)
        if role != "user":
            role = "model"
        content = message["content"]

        if type(content) == str:
            result.append({"role": role,
                           "parts": {
                               "text": content
                           }
                           })
        else:
            result.append({"role": role,
                               "parts": {
                                   "inline_data": content
                               }
                           })

    print("messages:", "\n\n\n".join([str(r) for r in result]))

    return result