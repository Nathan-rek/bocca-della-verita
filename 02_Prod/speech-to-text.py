
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Modèle français
MODEL_PATH = "./vosk-model-small-fr-0.22"
SAMPLE_RATE = 16000

print("Chargement du modèle français...")
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

print("\nReconnaissance vocale prête !")
print("Parle dans le micro : le texte apparaîtra ci-dessous.")
print("Appuie sur Ctrl+C pour arrêter.\n")


def callback(indata, frames, time_info, status):
    if status:
        print(f"Audio : {status}")

    data = bytes(indata)

    if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").strip()

        if text:
            print(f"Tu as dit : {text}", flush=True)


try:
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        while True:
            sd.sleep(1000)

except KeyboardInterrupt:
    # Affiche aussi les derniers mots reconnus
    result = json.loads(recognizer.FinalResult())
    text = result.get("text", "").strip()

    if text:
        print(f"Tu as dit : {text}")

    print("\nReconnaissance arrêtée.")

except Exception as error:
    print(f"\nErreur micro : {error}")
