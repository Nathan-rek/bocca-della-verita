import requests
import subprocess

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "jakobina:latest"

messages = [
    {
        "role": "system",
        "content": (
            "Tu es Amandine, un personnage qui semble déprimé. "
            "Tu réponds en français, naturellement, avec des réponses "
            "plutôt courtes. Tu ne prétends pas être une intelligence artificielle."
        )
    }
]

print("Conversation avec Amandine")
print("Tape 'quitter' pour terminer.\n")

while True:
    try:
        user_text = input("Toi : ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nFin de la conversation.")
        break

    if not user_text:
        continue

    if user_text.lower() == "quitter":
        print("Fin de la conversation.")
        break

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
        messages.append({
            "role": "assistant",
            "content": answer
        })

        print(f"\nAmandine : {answer}\n")

        subprocess.run(
            ["espeak-ng", "-v", "fr", "-s", "155", answer],
            check=False
        )

    except requests.RequestException as error:
        print(f"Erreur de connexion à Ollama : {error}")
        if messages and messages[-1]["role"] == "user":
            messages.pop()
