# Задача 25
filename = "task.txt"

with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 2:
            name = parts[0].strip()
            score = parts[1].strip()
            print(f"Имя: {name}, Оценка: {score}")