import os

FILENAME = "tasks.txt"

def show_tasks():
    if not os.path.exists(FILENAME):
        return []
    
    with open(FILENAME, "r", encoding="utf-8") as file:
        tasks = [line.strip() for line in file if line.strip()]
        
    if not tasks:
        print("\nСписок задач пока пусттт.")
        return []
        
    print("\nСписок задач:")
    for idx, task in enumerate(tasks, 1):
        print(f"{idx}. {task}")
    return tasks

def add_task():
    task = input("\nВведите новую задачу: ").strip()
    if task:
        with open(FILENAME, "a", encoding="utf-8") as file:
            file.write(task + "\n")
        print("Задача добавлена иууу!")

def delete_task():
    tasks = show_tasks()
    if not tasks:
        return
        
    try:
        choice = int(input("\nВведите номер выполненной задачи для удаления: "))
        if 1 <= choice <= len(tasks):
            removed = tasks.pop(choice - 1)
            with open(FILENAME, "w", encoding="utf-8") as file:
                for task in tasks:
                    file.write(task + "\n")
            print(f"Задача '{removed}' удалена.")
        else:
            print("Неверный номер задачи.")
    except ValueError:
        print("введите число.")

def main():
    while True:
        print("\n--- Органайзер задач ---")
        print("1. Посмотреть задачи")
        print("2. Добавить задачу")
        print("3. Удалить задачу")
        print("4. выйди отсюда")
        
        choice = input("Выберите пункт: ").strip()
        
        if choice == "1":
            show_tasks()
        elif choice == "2":
            add_task()
        elif choice == "3":
            delete_task()
        elif choice == "4":
            break
        else:
            print("Неверный выбор.")

if __name__ == "__main__":
    main()