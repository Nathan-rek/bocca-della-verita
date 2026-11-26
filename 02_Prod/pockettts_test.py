from pocket_tts import TTSModel
import scipy.io.wavfile

# Charger le modèle pré-entraîné
print("Chargement de Pocket TTS...")
tts = TTSModel.load_model()

# Charger la voix de Jakobina
print("Analyse de la voix de Jakobina...")
voice = tts.get_state_for_audio_prompt(
    "jakobina_refs/Son 05.wav"
)

# Générer une phrase en français
print("Génération de la voix...")
audio = tts.generate_audio(
    voice,
    "Bonjour ! Je suis Jakobina, comment puis-je vous aider ?"
)

# Enregistrer le résultat
scipy.io.wavfile.write(
    "jakobina_pocket_test.wav",
    tts.sample_rate,
    audio.numpy()
)

print("Terminé ! Fichier : jakobina_pocket_test.wav")
