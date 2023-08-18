def _speak():
    """
    Turn on voice output
    """
    from ._machinery import _context
    _context.voice = True

def _quiet():
    """
    Turn off voice output
    """
    from ._machinery import _context
    _context.voice = False

def _speak_out(text):
    """
    Speak out a string using Google Text To Speech
    """

    from gtts import gTTS
    from pydub import AudioSegment
    from pydub.playback import play
    import os

    # Convert text to audio using gTTS
    temp_filename = "temp_audio.mp3"
    tts = gTTS(text=text, lang="en", )
    tts.save(temp_filename)

    # Load audio into pydub
    audio_segment = AudioSegment.from_mp3(temp_filename)

    silence = AudioSegment.silent(duration=500)  # 500ms of silence

    audio_with_silence = silence + audio_segment

    # Remove the temporary file
    os.remove(temp_filename)

    # Play audio
    play(audio_with_silence)