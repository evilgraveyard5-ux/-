import json

profile_data = {
    "name": "Джиган",
    "age": 29,
    "city": "Вашингтон",
    "occupation": "Разраб",
    "skills": ["Python", "Git", "JSON"]
}

with open("profile.json", "w", encoding="utf-8") as file:
    json.dump(profile_data, file, ensure_ascii=False, indent=4)