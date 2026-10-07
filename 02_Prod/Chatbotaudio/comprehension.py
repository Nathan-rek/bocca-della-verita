from pathlib import Path

dossier = Path("C:/Users/prost/OneDrive/Documents/Projet/harald/02_Prod/Chatbotaudio")

for element in dossier.iterdir():
    if element.is_file():
        print(element.name)
        
file = open('marcel.txt')

file_contents = file.read()

print(file_contents)
    