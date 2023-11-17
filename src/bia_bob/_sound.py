class Internal:
    _microphone = None

def listen(mic_index: int = None):
    """Listens to the microphone and forwards the prompt to Bob."""
    from ._machinery import bob
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
            raise Exception("Error initializing the microphone. Please install whisper-mic: https://github.com/mallorbc/whisper_mic#setup")

    prompt = Internal._microphone.listen()
    print("You said: " + prompt)
    return bob(prompt)

