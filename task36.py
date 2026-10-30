import json

with open("profile.json", "r", encoding="utf-8") as file:
    loaded_data = json.load(file)

for key, value in loaded_data.items():
    print(f"{key}: {value}")