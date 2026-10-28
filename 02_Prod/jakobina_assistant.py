
import time
import subprocess
import requests
import torch
import soundfile as sf

from qwen_tts import Qwen3TTSModel


# ==================================================
# CONFIGURATION
# ==================================================

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "jakobina:latest"

VOICE_SAMPLE = "jakobina_refs/Son 05.wav"
OUTPUT_AUDIO = "jakobina_reponse.wav"

# Remplace par la transcription EXACTE de Son 05.wav.
REF_TEXT = "REMPLACER PAR LES PAROLES EXACTES DE L'EXTRAIT"

LANGUAGE = "French"
MAX_TOKENS = 128


# ==================================================
# CHARGEMENT DE QWEN3-TTS
# ==================================================

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Float32 : tentative pour éviter les valeurs invalides
DTYPE = torch.float32

print(f"Chargement de Qwen3-TTS sur {DEVICE}...")

tts = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    device_map=DEVICE,
    dtype=DTYPE,
    attn_implementation="eager",
)

print("Préparation de la référence vocale...")

voice_prompt = tts.create_voice_clone_prompt(
    ref_audio=VOICE_SAMPLE,
    ref_text=REF_TEXT,
    x_vector_only_mode=False,
)

print("Voix de Jakobina prête !")


# ==================================================
# MÉMOIRE DE CONVERSATION
# ==================================================

messages = []


# ==================================================
# FONCTION : GÉNÉRER UNE RÉPONSE TEXTE
# ==================================================

def generate_text(question):
    messages.append({
        "role": "user",
        "content": question,
    })

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": MAX_TOKENS,
                },
            },
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()
        answer = data["message"]["content"].strip()

        if not answer:
            raise ValueError("Ollama a renvoyé une réponse vide.")

        messages.append({
            "role": "assistant",
            "content": answer,
        })

        return answer

    except Exception:
        # Retire la question si la génération a échoué.
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        raise


# ==================================================
# FONCTION : GÉNÉRER LA VOIX
# ==================================================

def generate_voice(text):
    print("Jakobina prépare sa voix...")

    start = time.time()

    wavs, sample_rate = tts.generate_voice_clone(
        text=text,
        language=LANGUAGE,
        voice_clone_prompt=voice_prompt,
    )

    if not wavs or len(wavs[0]) == 0:
        raise RuntimeError("Qwen3-TTS n'a produit aucun audio.")

    sf.write(
        OUTPUT_AUDIO,
        wavs[0],
        sample_rate,
    )

    print(f"[Synthèse vocale : {time.time() - start:.1f} s]")


# ==================================================
# BOUCLE PRINCIPALE
# ==================================================

print("\n===================================")
print("       JAKOBINA EST PRÊTE")
print("Tape 'quitter' pour arrêter.")
print("===================================\n")

while True:
    try:
        question = input("Toi > ").strip()

        if question.lower() in ("quitter", "exit", "quit"):
            print("Jakobina > À bientôt !")
            break

        if not question:
            continue

        # Génération du texte
        print("\nJakobina réfléchit...")
        start = time.time()

        answer = generate_text(question)

        print(f"\nJakobina > {answer}")
        print(f"[Réponse texte : {time.time() - start:.1f} s]")

        # Génération audio
        try:
            generate_voice(answer)

            print("Lecture audio...")

            subprocess.run(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "error",
                    OUTPUT_AUDIO,
                ],
                check=False,
            )

        except Exception as audio_error:
            print(f"\nErreur audio : {audio_error}")
            print("La réponse texte reste disponible.")

        print()

    except KeyboardInterrupt:
        print("\nArrêt demandé. À bientôt !")
        break

    except requests.exceptions.ConnectionError:
        print(
            "\nImpossible de joindre Ollama. "
            "Vérifie qu'il est lancé.\n"
        )

    except requests.exceptions.RequestException as error:
        print(f"\nErreur de communication avec Ollama : {error}\n")

    except Exception as error:
        print(f"\nErreur : {error}\n")
