import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Load the Vosk speech recognition model
model = Model("./vosk-model-small-en-us-0.15")

# Create the speech recognizer
recognizer = KaldiRecognizer(model, 44100)

print("Vosk is ready!")
print("Speak into the microphone.")
print("Press Ctrl+C to stop.")

def callback(indata, frames, time, status):
    if status:
        print("Audio status:", status)

    if recognizer.AcceptWaveform(bytes(indata)):
        result = json.loads(recognizer.Result())
        text = result.get("text", "")

        if text:
            print("You said:", text)

with sd.RawInputStream(
    device=0,
    samplerate=44100,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
):
    while True:
        pass
