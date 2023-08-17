def _listen():
    """
    Activate the microphone and listen to the user.
    The passed command is then executed.
    """
    result = _listen_to_microphone()
    if result:
        print("You said:", result)

        from ._machinery import bob
        bob(result)


def _listen_to_microphone():
    """Recognizes speech from microphone and return it as string"""
    import speech_recognition as sr

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        # Reducing the noise
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

        try:
            # Recognize the content
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print("Error calling the API; {0}".format(e))
            return None


