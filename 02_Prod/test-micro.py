
import pyaudio

audio = pyaudio.PyAudio()

print("\n=== TEST DU MICRO ===")
print("Périphériques audio disponibles :\n")

for i in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(
            f'[{i}] {info["name"]} '
            f'(entrées : {info["maxInputChannels"]})'
        )

print("\nTest d'enregistrement pendant 5 secondes...")

try:
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )

    print("🎤 PARLE MAINTENANT !")

    for _ in range(int(16000 / 1024 * 5)):
        data = stream.read(1024, exception_on_overflow=False)

    stream.stop_stream()
    stream.close()

    print("✅ Le micro a pu être ouvert et lu.")

except Exception as e:
    print(f"❌ Erreur micro : {e}")

finally:
    audio.terminate()
