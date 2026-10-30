filename = "task.txt"

total_score = 0
count = 0

with open(filename, "r", encoding="utf-8") as file:
    for line in file:
        parts = line.strip().split(",")
        
        if len(parts) == 2:
            name = parts[0].strip()
            score = float(parts[1].strip())
            
            total_score += score
            count += 1
            print(f"Студент: {name}, Оценка: {score}")

if count > 0:
    average_score = total_score / count
    print(f"\nСредний балл по всем студентам: {average_score:.2f}")
else:
    print("Файл пустой или походу данные записаны неправильно")