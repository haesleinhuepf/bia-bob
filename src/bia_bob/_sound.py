class Internal:
    _microphone = None

def listen(mic_index: int = None):
    """Listens to the microphone and forwards the prompt to Bob."""
    from ._machinery import bob
    prompt = get_microphone_input(mic_index)

    print("You said: " + prompt)
    return bob(prompt)


def get_microphone_input(mic_index: int = None):
    from pathlib import Path
    if Internal._microphone is None or mic_index is not None:
        try:
            from whisper_mic.whisper_mic import WhisperMic

            cache_dir = str(Path.home()).replace("\\", "/") + "/.cache/whisper"

            from ._machinery import Context
            if Context.verbose:
                print("Using whisper model in", cache_dir)

            Internal._microphone = WhisperMic(model_root=cache_dir, mic_index=mic_index)
        except:
            raise Exception(
                "Error initializing the microphone. Please install whisper-mic: https://github.com/mallorbc/whisper_mic#setup")

    return Internal._microphone.listen()


def discuss(mic_index: int = None):

    from ._utilities import generate_response_to_user, output_text
    from ._machinery import init_assistant, Context

    if Context.model is None:
        init_assistant()

    while True:
        user_input = get_microphone_input(mic_index=mic_index)

        print("You said: " + user_input)

        user_input = user_input + "\nUse matplotlib for showing images."

        if user_input is None or user_input == "" or "bye" in user_input.lower():
            break

        mic_index = None

        code, full_response = generate_response_to_user(Context.model, user_input)

        output_text(full_response)

        _, summary = generate_response_to_user(Context.model, "Summarize the following to a single sentence: \n\n" + full_response, system_prompt="")
        speak(summary)

        if code is not None:
            code = code.replace(".tiff", ".tif")
            exec(code, Context.variables)


def output_code(code):
    """Display code content in the notebook."""
    from IPython.display import display, Markdown
    from IPython.core.display import HTML

    display(HTML(f"""
    <details>
    <summary> Show code </summary>
    <pre>
    {code}
    </pre>
    </details>
    """))


def speak(text):
    from openai import OpenAI
    import os
    from pydub import AudioSegment
    from pydub.playback import play

    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    temp_filename = "temp_audio.mp3"
    response.stream_to_file(temp_filename)

    audio = AudioSegment.from_file(temp_filename, format="mp3")

    # Play the audio
    play(audio)

    os.remove(temp_filename)
