from pathlib import Path

dataset = Path("jakobina_dataset")
texts = Path("jakobina_refs")
rows = []

for wav in sorted((dataset / "wav").glob("*.wav")):
    txt = texts / (wav.stem + ".txt")

    if not txt.exists():
        print(f"MANQUANT : {txt}")
        continue

    text = txt.read_text(encoding="utf-8-sig").strip()
    text = " ".join(text.split())

    if not text:
        print(f"VIDE : {txt}")
        continue

    if "|" in text:
        print(f"CARACTÈRE | À CORRIGER : {txt}")
        continue

    rows.append(f"{wav.name}|{text}")

(dataset / "metadata.csv").write_text(
    "\n".join(rows) + ("\n" if rows else ""),
    encoding="utf-8"
)

print(f"\nLignes créées : {len(rows)}")
print("Fichier : jakobina_dataset/metadata.csv")
PY
