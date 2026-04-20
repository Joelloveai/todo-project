tasks = []

def show_menu():
    print("\n=== MY TO-DO LIST ===")
    print("1. Add task")
    print("2. View tasks")
    print("3. Delete task")
    print("4. Exit")

def add_task():
    task = input("What task do you want to add? ")
    tasks.append(task)
    print("Added:", task)

def view_tasks():
    if len(tasks) == 0:
        print("No tasks yet.")
    else:
        print("\nYour tasks:")
        for i in range(len(tasks)):
            print(i + 1, ".", tasks[i])

def delete_task():
    if len(tasks) == 0:
        print("No tasks to delete.")
        return
    view_tasks()
    try:
        num = int(input("Enter task number to delete: "))
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            print("Deleted:", removed)
        else:
            print("Invalid number.")
    except:
        print("Please enter a number.")

while True:
    show_menu()
    choice = input("Choose 1-4: ")

    if choice == "1":
        add_task()
    elif choice == "2":
        view_tasks()
    elif choice == "3":
        delete_task()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Try again.")