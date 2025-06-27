#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, TypeAlias
import re
from rich import print as rprint
from rich.style import Style
import argparse
import shutil
import json, yaml, toml

Section: TypeAlias = Dict[str, List[str]]

def print(*args, **kwargs):
    # Define your custom styles
    HEADING1_STYLE = Style(color="yellow", bold=True)
    HEADING2_STYLE = Style(color="green", bold=True)
    NUMBERED_STYLE = Style(color="cyan")
    """Custom print that styles #-lines and numbered lines using rich."""
    original_sep = kwargs.get("sep", " ")
    original_text: str = original_sep.join(str(arg) for arg in args)

    lines = original_text.split("\n")
    for line in lines:
        if line.startswith("# "):
            rprint(f"[{HEADING1_STYLE}]{line}[/]")
        elif line.startswith("## "):
            rprint(f"[{HEADING2_STYLE}]{line}[/]")
        elif line and line[0].isdigit():  # Check if first char is a digit
            rprint(f"[{NUMBERED_STYLE}]{line}[/]")
        else:
            rprint(line)  # Fallback to plain print


class TodoManager:
    def __init__(self, todo_path: Path, config_path: Path = "") -> None:
        self.__FilePath: Path = todo_path
        self.__ConfigPath: Path = config_path
        self.__TodoLists: Section = {}
        self.__DoneLists: Section = {}
        self.__Viewer:str = ""
        self.__Editor:str = ""
        self.__parseFile()
        self.__loadConfig()

    def __parseFile(self) -> None:
        file_lines: List[str] = []
        with open(self.__FilePath, "r") as f:
            for line in f:
                file_lines.append(line.strip())

            current_section: Section = {}
            for l in file_lines:
                if not l:
                    continue
                if l.startswith("# "):
                    section_name = l[2:].strip()
                    if section_name == "Todo":
                        current_section = self.__TodoLists
                    elif section_name == "Done":
                        current_section = self.__DoneLists
                    else:
                        print(f"Unknown section: {section_name}")
                        continue
                elif l.startswith("## "):
                    list_name = l[3:].strip()
                    current_section[list_name] = []
                else:
                    line_match = re.match(r"^\d+\.\s(.*)$", l.strip())
                    # plain text line will be treated as a task
                    task: str = line_match.group(1) if line_match else l
                    if list_name not in current_section:
                        print(f"Warning: Task '{task}' found without a list.")
                        continue
                    current_section[list_name].append(task)
    
    # TODO Implementation needed
    def __loadConfig(self)->None:
        with open(self.__ConfigPath, "r") as f:
            json.load(f)
            pass
        pass
    
    # TODO Implementation needed
    def __saveConfig(self)->None:
        config_type = self.__ConfigPath.suffix
        with open(self.__ConfigPath, "w") as f:
            if config_type == ".json":
                pass
            elif config_type == ".yml" or config_type == ".yaml":
                pass
            elif config_type == ".toml":
                pass
            pass
        pass

    def writeFile(self) -> None:
        with open(self.__FilePath, "w") as f:
            f.write("# Todo\n")
            for list_name, tasks in self.__TodoLists.items():
                f.write(f"## {list_name}\n")
                for i, task in enumerate(tasks, start=1):
                    f.write(f"{i}. {task}\n")
            f.write("\n# Done\n")
            for list_name, tasks in self.__DoneLists.items():
                f.write(f"## {list_name}\n")
                for i, task in enumerate(tasks, start=1):
                    f.write(f"{i}. {task}\n")

    # Check matching results.
    def __matchListName(self, list_name: str) -> List[str]:
        matched_name: List[str] = []
        for exist_list in self.__TodoLists:
            if list_name in exist_list:
                matched_name.append(exist_list)
        if matched_name:
            print(f"Possible list you'd like to refer to:")
            for i in range(len(matched_name)):
                name: str = matched_name[i]
                print(f"{i+1}. {name}")
            return matched_name
        else:
            print(f"No matching list found.")
            return []

    def __checkListName(self, list_name: str, no_create: bool = False) -> str:
        if list_name in self.__TodoLists:
            return list_name
        else:
            print(f"No such list named as '{list_name}'.")
            matched_name: List[str] = self.__matchListName(list_name)
            # Handle user input
            if matched_name:
                try:
                    selection: int = int(
                        input(
                            f"Use 0 for a new list {list_name}, simple <Enter> to abort\nYour selection: "
                        ).strip()
                    )
                    assert selection is not None
                    if selection == 0 and not no_create:
                        return list_name
                    elif selection > 0 and selection <= len(matched_name):
                        return matched_name[int(selection - 1)]
                    else:
                        print("Invalid input: out of range")
                        return ""
                except:
                    print("Invalid input, nothing changed.")
                    return ""
            elif not no_create:
                opt: str = input(f"Create a new list named as {list_name}? (y/N)")
                if opt.lower() == "y":
                    return list_name
                else:
                    print(f"No list created. Nothing changed")
            return ""

    # Add a new list if it does not exist without asking.
    def addList(self, list_name: str, quiet: bool = False) -> None:
        if list_name in self.__TodoLists:
            if not quiet:
                print(f"List '{list_name}' already exists. No new list created.")
            return
        else:
            self.__TodoLists[list_name] = []

    def addTask(self, list_name: str, task: str) -> None:
        granted_list_name = self.__checkListName(list_name)
        if granted_list_name:
            self.addList(granted_list_name, True)
            self.__TodoLists[granted_list_name].append(task)
            print(f"Added task '{task}' to list '{granted_list_name}'.")
        else:
            print(f"Cancelled adding task, nothing changed")
        return

    def orderTask(
        self, list_name: str, old_task_number: int, new_task_number: int
    ) -> None:
        list_name = self.__checkListName(list_name)
        if list_name:
            if old_task_number < 1 or old_task_number > len(self.__TodoLists[list_name]):
                print(f"Invalid task number {old_task_number} in list {list_name}.")
                return
            elif new_task_number < 1 or new_task_number > len(
                self.__TodoLists[list_name]
            ):
                print(f"Invalid new task number {new_task_number} in list {list_name}.")
                return
            else:
                task: str = self.__TodoLists[list_name].pop(old_task_number - 1)
                self.__TodoLists[list_name].insert(new_task_number - 1, task)
                print(
                    f"Moved task '{task}' from position {old_task_number} to {new_task_number} in list '{list_name}'."
                )
        return

    def __moveTask(
        self, source: Section, target: Section, list_name: str, task_number: int
    ) -> None:
        if list_name not in source:
            print(f"No such list named as {list_name}.")
            return
        if task_number < 1 or task_number > len(source[list_name]):
            print(f"Invalid task number {task_number} in list {list_name}.")
            return
        task: str = source[list_name].pop(task_number - 1)
        if list_name in target:
            target[list_name].append(task)
        else:
            target[list_name] = [task]

    def __moveList(self, source: Section, target: Section, list_name: str) -> None:
        if list_name not in source:
            print(f"No such list named as {list_name}.")
            return
        target[list_name] = source.pop(list_name)

    # Not implemented yet
    def doneList(self, list_name: str) -> None:
        self.__moveList(self.__TodoLists, self.__DoneLists, list_name)
        print(f"Done list '{list_name}'")

    def restoreList(self, list_name: str) -> None:
        self.__moveList(self.__DoneLists, self.__TodoLists, list_name)
        print(f"Restore list '{list_name}' to Todo section.")

    def doneTask(self, list_name: str, task_number: int) -> None:
        self.__moveTask(self.__TodoLists, self.__DoneLists, list_name, task_number)
        print(f"Done task {task_number} in list '{list_name}'.")

    def restoreTask(self, list_name: str, task_number: int) -> None:
        self.__moveTask(self.__DoneLists, self.__TodoLists, list_name, task_number)
        print(f"Restored task {task_number} in list '{list_name}' to Todo section.")

    def clearDoneList(self, force: bool = False) -> None:
        if force:
            self.__DoneLists = {}
            print("Cleared all done tasks and lists.")
        else:
            opt = input(
                "Are you sure to delete all the done tasks and done lists? (y/N): "
            )
            if opt.lower() == "y":
                self.__DoneLists = {}
                print("Cleared.")
            else:
                print("Abort. Done list not modified.")
        return

    def __viewSection(self, section: Section) -> None:
        for list_name, tasks in section.items():
            print(f"\n## {list_name}\n")
            for i, task in enumerate(tasks, start=1):
                print(f"{i}. {task}")
        return

    def __viewList(self, section: Section, list_name: str) -> None:
        list_name = self.__checkListName(list_name, no_create=True)
        print(f"\n## {list_name}\n")
        for i, task in enumerate(section[list_name], start=1):
            print(f"{i}. {task}")
        return

    # ----------------------------------
    # Visualize the todo lists and tasks
    # ----------------------------------
    def viewTodo(self) -> None:
        print("# Todo")
        self.__viewSection(self.__TodoLists)

    def viewTodoList(self, list_name: str) -> None:
        self.__viewList(self.__TodoLists, list_name)

    def viewDone(self) -> None:
        print("# Done")
        self.__viewSection(self.__DoneLists)

    def viewDoneList(self, list_name: str) -> None:
        self.__viewList(self.__DoneLists, list_name)

    def viewAll(self) -> None:
        self.viewTodo()
        print("")
        self.viewDone()


# ----------------------
def create_parser():
    """Create and configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="A command-line todo list manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s view                           # View all todo and done items
  %(prog)s view --todo                    # View only todo items
  %(prog)s view --done                    # View only done items
  %(prog)s view --list "My List"          # View specific list
  %(prog)s add "My List" "Buy groceries"  # Add task to list
  %(prog)s add-list "New List"            # Add new list
  %(prog)s done "My List" 1               # Mark task 1 as done
  %(prog)s restore "My List" 2            # Restore task 2 from done
  %(prog)s order "My List" 1 3            # Move task from position 1 to 3
  %(prog)s clear-done                     # Clear all done items

        """,
    )

    # Global options
    parser.add_argument(
        "--file",
        "-f",
        type=Path,
        help="Path to the todo file (default: ~/TODO.md or ./TODO.md in debug mode)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Use current directory for todo file instead of home directory",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # View command
    view_parser = subparsers.add_parser("view", help="View todo lists and tasks")
    view_group = view_parser.add_mutually_exclusive_group()
    view_group.add_argument("--todo", action="store_true", help="Show only todo items")
    view_group.add_argument("--done", action="store_true", help="Show only done items")
    view_group.add_argument("--list", "-l", help="Show specific list")

    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task to a list")
    add_parser.add_argument("list_name", help="Name of the list")
    add_parser.add_argument("task", help="Task description")

    # Add list command
    add_list_parser = subparsers.add_parser("add-list", help="Add a new list")
    add_list_parser.add_argument("list_name", help="Name of the new list")

    # Done task command
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("list_name", help="Name of the list")
    done_parser.add_argument(
        "task_number", type=int, help="Task number to mark as done"
    )

    # Done list command
    done_list_parser = subparsers.add_parser(
        "done-list", help="Mark entire list as done"
    )
    done_list_parser.add_argument("list_name", help="Name of the list to mark as done")

    # Restore task command
    restore_parser = subparsers.add_parser(
        "restore", help="Restore a done task back to todo"
    )
    restore_parser.add_argument("list_name", help="Name of the list")
    restore_parser.add_argument("task_number", type=int, help="Task number to restore")

    # Restore list command
    restore_list_parser = subparsers.add_parser(
        "restore-list", help="Restore entire done list back to todo"
    )
    restore_list_parser.add_argument("list_name", help="Name of the list to restore")

    # Order/reorder task command
    order_parser = subparsers.add_parser("order", help="Reorder tasks within a list")
    order_parser.add_argument("list_name", help="Name of the list")
    order_parser.add_argument(
        "old_position", type=int, help="Current position of the task"
    )
    order_parser.add_argument(
        "new_position", type=int, help="New position for the task"
    )

    # Clear done command
    clear_parser = subparsers.add_parser(
        "clear", help="Clear all done tasks and lists"
    )
    clear_parser.add_argument(
        "--force", "-f", action="store_true", help="Force clear without confirmation"
    )

    # Save command
    save_parser = subparsers.add_parser("save", help="Save current state to file")
    
    config_parser = subparsers.add_parser("config", help="Config this small tool")
    config_parser.add_argument("editor", type=str, help="Config default editor")
    config_parser.add_argument("file", type=str, help="Config default path of 'TODO.md'")
    config_parser.add_argument("printer",type=str, help="Config default printer of todo-list")

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Determine the todo file path
    if args.file:
        todo_file = args.file
    elif args.debug:
        todo_file = Path(__file__).resolve().parent / "TODO.md"
    else:
        todo_file = Path.home() / "TODO.md"

    # Create TodoManager instance
    try:
        tdmgr = TodoManager(todo_file)
    except FileNotFoundError:
        print(f"Todo file not found at {todo_file}")
        print("Creating new todo file...")
        todo_file.touch()
        # Create an empty todo file with basic structure
        with open(todo_file, "w") as f:
            f.write("# Todo\n\n# Done\n")
        tdmgr = TodoManager(todo_file)

    # Handle different commands
    if not args.command:
        tdmgr.viewTodo()
    elif args.command == "view":
        if args.todo:
            tdmgr.viewTodo()
        elif args.done:
            tdmgr.viewDone()
        elif args.list:
            # Try to find the list in both todo and done sections
            if args.list in tdmgr.__TodoLists:
                tdmgr.viewTodoList(args.list)
            elif args.list in tdmgr.__DoneLists:
                tdmgr.viewDoneList(args.list)
            else:
                print(f"List '{args.list}' not found")
                return
        else:
            tdmgr.viewAll()

    elif args.command == "add":
        tdmgr.addTask(args.list_name, args.task)
        tdmgr.writeFile()

    elif args.command == "add-list":
        tdmgr.addList(args.list_name)
        tdmgr.writeFile()

    elif args.command == "done":
        tdmgr.doneTask(args.list_name, args.task_number)
        tdmgr.writeFile()

    elif args.command == "done-list":
        tdmgr.doneList(args.list_name)
        tdmgr.writeFile()

    elif args.command == "restore":
        tdmgr.restoreTask(args.list_name, args.task_number)
        tdmgr.writeFile()

    elif args.command == "restore-list":
        tdmgr.restoreList(args.list_name)
        tdmgr.writeFile()

    elif args.command == "order":
        tdmgr.orderTask(args.list_name, args.old_position, args.new_position)
        tdmgr.writeFile()

    elif args.command == "clear-done":
        force = getattr(args, "force", False)
        tdmgr.clearDoneList(force)
        tdmgr.writeFile()

    elif args.command == "save":
        tdmgr.writeFile()
        print("Todo file saved.")


if __name__ == "__main__":
    main()
