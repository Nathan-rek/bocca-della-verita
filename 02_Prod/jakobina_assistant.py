import time
import requests
from TTS.api import TTS

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "jakobina:latest"
VOICE_SAMPLE = "jakobina_refs/Son 05.wav"
OUTPUT_AUDIO = "jakobina_reponse.wav"

print("Chargement de la voix de Jakobina...")
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2"
).to("cpu")
print("Jakobina est prête !")

messages = []

print("\nConversation lancée. Tape 'quitter' pour arrêter.\n")

while True:
    try:
        question = input("Toi > ").strip()

        if question.lower() in ("quitter", "exit", "quit"):
            print("Jakobina > À bientôt.")
            break

        if not question:
            continue

        messages.append({"role": "user", "content": question})

        start = time.time()
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=300
        )
        response.raise_for_status()

        answer = response.json()["message"]["content"].strip()
        messages.append({"role": "assistant", "content": answer})

        print(f"\nJakobina > {answer}")
        print(f"[Réponse texte : {time.time() - start:.1f} s]")

        print("Jakobina prépare sa voix...")
        tts.tts_to_file(
            text=answer,
            speaker_wav=VOICE_SAMPLE,
            language="fr",
            file_path=OUTPUT_AUDIO
        )

        print("Lecture audio...")
        import subprocess
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "error",
             OUTPUT_AUDIO],
            check=False
        )
        print()

    except KeyboardInterrupt:
        print("\nArrêt demandé.")
        break
    except Exception as error:
        print(f"\nErreur : {error}")
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        print("Tu peux réessayer.\n")
