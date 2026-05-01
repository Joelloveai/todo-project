#!/usr/bin/env python3
"""
- Persistent storage (tasks.json)
- Priorities, due dates, completion toggle
- Edit tasks, search, sort, statistics
- Colorful terminal output
"""

import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional

# ----- ANSI color codes -----
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
DIM = "\033[2m"

# Priority symbols and colors
PRIORITIES = {
    "high": {"symbol": "🔴", "color": RED, "name": "High"},
    "medium": {"symbol": "🟡", "color": YELLOW, "name": "Medium"},
    "low": {"symbol": "🟢", "color": GREEN, "name": "Low"},
}

DATA_FILE = "tasks.json"


def load_tasks() -> List[Dict]:
    """Load tasks from JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            # Ensure old tasks have all keys (for upgrades)
            for t in tasks:
                t.setdefault("completed", False)
                t.setdefault("priority", "medium")
                t.setdefault("due_date", None)
            return tasks
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks: List[Dict]) -> None:
    """Save tasks to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(text: str):
    """Print a styled header."""
    print(f"\n{BOLD}{CYAN}═══ {text} ═══{RESET}")


def get_valid_date(prompt: str) -> Optional[str]:
    """Ask user for a date in YYYY-MM-DD format. Return None if skipped."""
    print(f"{DIM}{prompt} (YYYY-MM-DD, leave empty to skip){RESET}")
    date_str = input("> ").strip()
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        print(f"{RED}Invalid date format. Use YYYY-MM-DD.{RESET}")
        return get_valid_date(prompt)


def get_priority() -> str:
    """Ask user for priority (high/medium/low)."""
    print(
        f"Priority: {PRIORITIES['high']['symbol']} high  {PRIORITIES['medium']['symbol']} medium  {PRIORITIES['low']['symbol']} low"
    )
    while True:
        p = input("> ").strip().lower()
        if p in PRIORITIES:
            return p
        print(f"{RED}Invalid priority. Choose high, medium, or low.{RESET}")


def add_task(tasks: List[Dict]) -> None:
    """Add a new task."""
    print_header("ADD NEW TASK")
    title = input("Task title: ").strip()
    if not title:
        print(f"{RED}Task title cannot be empty.{RESET}")
        return
    priority = get_priority()
    due_date = get_valid_date("Due date")
    tasks.append(
        {"title": title, "completed": False, "priority": priority, "due_date": due_date}
    )
    save_tasks(tasks)
    print(f"{GREEN}✓ Task added!{RESET}")


def print_task(index: int, task: Dict, show_index: bool = True):
    """Print a single task with colors and status."""
    status = f"{GREEN}✓{RESET}" if task["completed"] else f"{RED}✗{RESET}"
    priority_info = PRIORITIES[task["priority"]]
    priority_str = f"{priority_info['color']}{priority_info['symbol']} {priority_info['name']}{RESET}"
    due = ""
    if task["due_date"]:
        due_date_obj = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        today = date.today()
        if due_date_obj < today and not task["completed"]:
            due = f"{RED} (overdue: {task['due_date']}){RESET}"
        else:
            due = f"{DIM}(due: {task['due_date']}){RESET}"
    title = task["title"]
    if task["completed"]:
        title = f"{DIM}{title}{RESET}"
    else:
        title = f"{BOLD}{title}{RESET}"
    index_str = f"{index}. " if show_index else ""
    print(f"{index_str}[{status}] {priority_str} {title} {due}")


def view_tasks(tasks: List[Dict]):
    """Display all tasks with sorting options."""
    if not tasks:
        print(f"\n{YELLOW}No tasks yet. Add some!{RESET}")
        return
    print_header("VIEW TASKS")
    print("Sort by: 1) Priority & due date  2) Completion status  3) Creation order")
    sort_choice = input("Choose (1/2/3) [default=1]: ").strip() or "1"
    if sort_choice == "1":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                priority_order[t["priority"]],
                t.get("due_date") or "9999-12-31",
            ),
        )
    elif sort_choice == "2":
        sorted_tasks = sorted(
            tasks, key=lambda t: (t["completed"], t.get("due_date") or "9999-12-31")
        )
    else:
        sorted_tasks = tasks[:]  # preserve original order

    for i, task in enumerate(sorted_tasks, start=1):
        print_task(i, task)


def delete_task(tasks: List[Dict]):
    """Delete a task by number."""
    if not tasks:
        print(f"{YELLOW}No tasks to delete.{RESET}")
        return
    view_tasks(tasks)
    try:
        num = int(input(f"\n{BOLD}Enter task number to delete: {RESET}"))
        if 1 <= num <= len(tasks):
            removed = tasks.pop(num - 1)
            save_tasks(tasks)
            print(f"{GREEN}✓ Deleted: {removed['title']}{RESET}")
        else:
            print(f"{RED}Invalid number.{RESET}")
    except ValueError:
        print(f"{RED}Please enter a number.{RESET}")


def toggle_complete(tasks: List[Dict]):
    """Mark/unmark a task as completed."""
    if not tasks:
        print(f"{YELLOW}No tasks to modify.{RESET}")
        return
    view_tasks(tasks)
    try:
        num = int(input(f"\n{BOLD}Enter task number to toggle completion: {RESET}"))
        if 1 <= num <= len(tasks):
            tasks[num - 1]["completed"] = not tasks[num - 1]["completed"]
            save_tasks(tasks)
            status = "completed" if tasks[num - 1]["completed"] else "pending"
            print(f"{GREEN}✓ Task marked as {status}.{RESET}")
        else:
            print(f"{RED}Invalid number.{RESET}")
    except ValueError:
        print(f"{RED}Please enter a number.{RESET}")


def edit_task(tasks: List[Dict]):
    """Edit an existing task (title, priority, due date)."""
    if not tasks:
        print(f"{YELLOW}No tasks to edit.{RESET}")
        return
    view_tasks(tasks)
    try:
        num = int(input(f"\n{BOLD}Enter task number to edit: {RESET}"))
        if 1 <= num <= len(tasks):
            task = tasks[num - 1]
            print_header(f"EDITING: {task['title']}")
            new_title = input(
                f"New title (leave empty to keep '{task['title']}'): "
            ).strip()
            if new_title:
                task["title"] = new_title
            print(f"Current priority: {PRIORITIES[task['priority']]['name']}")
            new_priority = (
                input("New priority (high/medium/low, leave empty to keep): ")
                .strip()
                .lower()
            )
            if new_priority in PRIORITIES:
                task["priority"] = new_priority
            new_due = get_valid_date("New due date (leave empty to keep current)")
            if new_due is not None:
                task["due_date"] = new_due
            save_tasks(tasks)
            print(f"{GREEN}✓ Task updated!{RESET}")
        else:
            print(f"{RED}Invalid number.{RESET}")
    except ValueError:
        print(f"{RED}Please enter a number.{RESET}")


def search_tasks(tasks: List[Dict]):
    """Search tasks by keyword in title."""
    keyword = input("Enter search keyword: ").strip().lower()
    if not keyword:
        print(f"{YELLOW}No keyword entered.{RESET}")
        return
    results = [t for t in tasks if keyword in t["title"].lower()]
    if not results:
        print(f"{YELLOW}No matching tasks.{RESET}")
    else:
        print_header(f"SEARCH RESULTS FOR '{keyword}'")
        for i, task in enumerate(results, start=1):
            print_task(i, task)


def show_statistics(tasks: List[Dict]):
    """Show task statistics: total, completed, completion rate, overdue."""
    total = len(tasks)
    if total == 0:
        print(f"\n{YELLOW}No tasks yet.{RESET}")
        return
    completed = sum(1 for t in tasks if t["completed"])
    rate = (completed / total) * 100
    today = date.today()
    overdue = 0
    for t in tasks:
        if t["due_date"] and not t["completed"]:
            due = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
            if due < today:
                overdue += 1
    print_header("STATISTICS DASHBOARD")
    print(f"{CYAN}Total tasks:   {total}{RESET}")
    print(f"{GREEN}Completed:     {completed}{RESET}")
    print(f"{RED}Pending:       {total - completed}{RESET}")
    print(f"{YELLOW}Completion:    {rate:.1f}%{RESET}")
    print(f"{MAGENTA}Overdue:       {overdue}{RESET}")
    # Priority breakdown
    high = sum(1 for t in tasks if t["priority"] == "high")
    medium = sum(1 for t in tasks if t["priority"] == "medium")
    low = sum(1 for t in tasks if t["priority"] == "low")
    print(f"{PRIORITIES['high']['symbol']} High priority: {high}")
    print(f"{PRIORITIES['medium']['symbol']} Medium: {medium}")
    print(f"{PRIORITIES['low']['symbol']} Low: {low}")


def main():
    tasks = load_tasks()
    while True:
        clear_screen()
        print(f"{BOLD}{CYAN}╔══════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{CYAN}║        ADVANCED TO-DO LIST           ║{RESET}")
        print(f"{BOLD}{CYAN}╚══════════════════════════════════════╝{RESET}")
        print(f"\n{BOLD}Available commands:{RESET}")
        print(f"  {GREEN}[1]{RESET} Add task")
        print(f"  {GREEN}[2]{RESET} View tasks")
        print(f"  {GREEN}[3]{RESET} Delete task")
        print(f"  {GREEN}[4]{RESET} Toggle complete")
        print(f"  {GREEN}[5]{RESET} Edit task")
        print(f"  {GREEN}[6]{RESET} Search tasks")
        print(f"  {GREEN}[7]{RESET} Statistics")
        print(f"  {GREEN}[8]{RESET} Exit")
        choice = input(f"\n{BOLD}Your choice (1-8): {RESET}").strip()
        if choice == "1":
            add_task(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "2":
            view_tasks(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "3":
            delete_task(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "4":
            toggle_complete(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "5":
            edit_task(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "6":
            search_tasks(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "7":
            show_statistics(tasks)
            input(f"{DIM}Press Enter to continue...{RESET}")
        elif choice == "8":
            print(f"\n{GREEN}Goodbye! Stay productive.{RESET}")
            break
        else:
            print(f"{RED}Invalid choice. Press Enter to try again.{RESET}")
            input()


if __name__ == "__main__":
    main()
