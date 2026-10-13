
import json
import subprocess
import requests
import pyaudio
import threading

from pynput import keyboard
from vosk import Model, KaldiRecognizer

# Configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "jakobina:latest"
VOSK_MODEL_PATH = "vosk-model-small-fr-0.22"

SAMPLE_RATE = 16000
CHUNK_SIZE = 4000

# État de l'enregistrement
enregistrement_actif = False
traitement_en_cours = False
blocs_audio = []
verrou = threading.Lock()
arret_demande = False

# Initialisation
print("Chargement du modèle Vosk...")
vosk_model = Model(VOSK_MODEL_PATH)
audio = pyaudio.PyAudio()

messages = []


def enregistrer():
    """Enregistre le microphone pendant que M est activée."""
    global enregistrement_actif, blocs_audio

    stream = None

    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )

        print("🎤 Enregistrement démarré.")

        while True:
            with verrou:
                actif = enregistrement_actif

            if not actif:
                break

            data = stream.read(
                CHUNK_SIZE,
                exception_on_overflow=False
            )

            with verrou:
                if enregistrement_actif:
                    blocs_audio.append(data)

    except Exception as error:
        print(f"Erreur micro : {error}")

    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()

        with verrou:
            enregistrement_actif = False
            donnees = b"".join(blocs_audio)

        if donnees:
            traiter_audio(donnees)
        else:
            print("Aucun son enregistré.")


def traiter_audio(donnees):
    """Transcrit l'audio, demande une réponse à Jakobina et la lit."""
    global traitement_en_cours

    with verrou:
        traitement_en_cours = True

    try:
        recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
        recognizer.AcceptWaveform(donnees)
        resultat = json.loads(recognizer.FinalResult())
        phrase = resultat.get("text", "").strip()

        if not phrase:
            print("Je n'ai pas compris. Réessaie en appuyant sur M.")
            return

        print(f"\nToi : {phrase}")

        if phrase.lower().strip(" .!?") in (
            "quitter",
            "arrêter",
            "arrêter la conversation",
            "stop"
        ):
            print("Fin de la conversation.")
            return

        answer = demander_a_jakobina(phrase)

        if answer:
            print(f"\nJakobina : {answer}")
            parler(answer)

        print("\nAppuie sur M pour parler à nouveau.")

    except Exception as error:
        print(f"Erreur de traitement audio : {error}")

    finally:
        with verrou:
            traitement_en_cours = False


def demander_a_jakobina(user_text):
    """Envoie la phrase à Ollama."""
    messages.append({
        "role": "user",
        "content": user_text
    })

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=180
        )
        response.raise_for_status()

        answer = response.json()["message"]["content"].strip()

        if not answer:
            answer = "Je n'ai rien à dire."

        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except requests.RequestException as error:
        print(f"Erreur de connexion à Ollama : {error}")
        messages.pop()
        return None


def parler(texte):
    """Fait parler Jakobina."""
    subprocess.run(
        ["espeak-ng", "-v", "fr", "-s", "145", texte],
        check=False
    )


def touche_pressee(key):
    """M démarre ou arrête l'enregistrement sans Entrée."""
    global enregistrement_actif, blocs_audio, arret_demande

    try:
        est_m = key.char and key.char.lower() == "m"
    except AttributeError:
        est_m = False

    if not est_m:
        return

    with verrou:
        if arret_demande or traitement_en_cours:
            return

        if not enregistrement_actif:
            blocs_audio = []
            enregistrement_actif = True
            action = "demarrer"
        else:
            enregistrement_actif = False
            action = "terminer"

    if action == "demarrer":
        threading.Thread(
            target=enregistrer,
            daemon=True
        ).start()
    else:
        print("\n⏹️ Fin de l'enregistrement...")


def touche_relachee(key):
    """Évite que la touche M maintenue ne déclenche plusieurs actions."""
    return


print("\n=== Conversation vocale avec Jakobina ===")
print("M : commencer ou terminer ta phrase")
print("Ctrl+C : quitter")
print("Parle uniquement entre les deux appuis sur M.\n")

listener = keyboard.Listener(on_press=touche_pressee)
listener.start()

try:
    while listener.is_alive():
        listener.join(timeout=0.2)

except KeyboardInterrupt:
    print("\nArrêt de la conversation.")

finally:
    with verrou:
        arret_demande = True
        enregistrement_actif = False

    listener.stop()
    audio.terminate()
