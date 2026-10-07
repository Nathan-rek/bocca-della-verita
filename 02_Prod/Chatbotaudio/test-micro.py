import sounddevice as sd
import numpy as np

DEVICE = 1
DURATION = 5
SAMPLE_RATE = 44100

print("Test du micro...")
print("Parle dans ton casque pendant 5 secondes.")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    device=DEVICE
)

sd.wait()

volume = np.max(np.abs(audio))

print()
print("Test terminé.")
print("Volume maximum détecté :", volume)

if volume < 0.01:
    print("❌ Très peu ou pas de signal micro.")
else:
    print("✅ Le micro reçoit bien du son !")