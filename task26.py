filename = "task.txt"
total = 0
count = 0

with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 2:
            total += float(parts[1].strip())
            count += 1

if count > 0:
    print(f"Средний балл: {total / count:.2f}")