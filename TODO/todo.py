#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional, List
import re
from rich import print as rprint
from rich.style import Style
import argparse
import shutil
import json

type Section = Dict[str, List[str]]


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
    def __init__(self, todo_path: Path) -> None:
        self.FilePath: Path = todo_path
        self.TodoLists: Section = {}
        self.DoneLists: Section = {}
        self.__parseFile()

    def __parseFile(self) -> None:
        file_lines: List[str] = []
        with open(self.FilePath, "r") as f:
            for line in f:
                file_lines.append(line.strip())

            current_section: Section = {}
            for l in file_lines:
                if not l:
                    continue
                if l.startswith("# "):
                    section_name = l[2:].strip()
                    if section_name == "Todo":
                        current_section = self.TodoLists
                    elif section_name == "Done":
                        current_section = self.DoneLists
                    else:
                        print(f"Unknown section: {section_name}")
                        continue
                elif l.startswith("## "):
                    list_name = l[3:].strip()
                    current_section[list_name] = []
                else:
                    line_match = re.match(r"^\d+\.\s(.*)$", l.strip())
                    # plain text line will be treated as a task
                    task: str = line_match.group(1) if line_match else l.strip()
                    current_section[list_name].append(task)

    def writeFile(self) -> None:
        with open(self.FilePath, "w") as f:
            f.write("# Todo\n")
            for list_name, tasks in self.TodoLists.items():
                f.write(f"## {list_name}\n")
                for i, task in enumerate(tasks, start=1):
                    f.write(f"{i}. {task}\n")
            f.write("\n# Done\n")
            for list_name, tasks in self.DoneLists.items():
                f.write(f"## {list_name}\n")
                for i, task in enumerate(tasks, start=1):
                    f.write(f"{i}. {task}\n")

    # Check matching results.
    def __matchListName(self, list_name: str) -> List[str]:
        matched_name: List[str] = []
        for exist_list in self.TodoLists:
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

    def __checkListName(self, list_name: str, no_create:bool=False) -> str:
        if list_name in self.TodoLists:
            return list_name
        else:
            print(f"No such list named as '{list_name}'.")
            matched_name: List[str] = self.__matchListName(list_name)
            # Handle user input
            if matched_name:
                try:
                    selection: int = int(input(f"Use 0 for a new list {list_name}, simple <Enter> to abort\nYour selection: ").strip())
                    assert selection is not None
                    if selection == 0 and not no_create:
                        return list_name
                    elif selection > 0 and selection <= len(matched_name):
                        return matched_name[int(selection - 1)]
                    else:
                        print("Invalid input: out of range")
                        exit(1)
                except:
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
        if list_name in self.TodoLists:
            if not quiet:
                print(f"List '{list_name}' already exists. No new list created.")
            return
        else:
            self.TodoLists[list_name] = []

    def addTask(self, list_name: str, task: str) -> None:
        granted_list_name = self.__checkListName(list_name)
        if granted_list_name:
            self.addList(granted_list_name, True)
            self.TodoLists[granted_list_name].append(task)
            print(f"Added task '{task}' to list '{granted_list_name}'.")
        else:
            print(f"Cancelled adding task, nothing changed")
        return

    def orderTask(
        self, list_name: str, old_task_number: int, new_task_number: int
    ) -> None:
        list_name = self.__checkListName(list_name)
        if list_name:
            if old_task_number < 1 or old_task_number > len(self.TodoLists[list_name]):
                print(f"Invalid task number {old_task_number} in list {list_name}.")
                return
            elif new_task_number < 1 or new_task_number > len(
                self.TodoLists[list_name]
            ):
                print(f"Invalid new task number {new_task_number} in list {list_name}.")
                return
            else:
                task: str = self.TodoLists[list_name].pop(old_task_number - 1)
                self.TodoLists[list_name].insert(new_task_number - 1, task)
                print(
                    f"Moved task '{task}' from position {old_task_number} to {new_task_number} in list '{list_name}'."
                )
        return
    
    def __moveTask(self, source: Section, target: Section, list_name: str, task_number: int) -> None:
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
        self.__moveList(self.TodoLists, self.DoneLists, list_name)
        print(f"Done list '{list_name}'")

    def restoreList(self, list_name: str) -> None:
        self.__moveList(self.DoneLists, self.TodoLists, list_name)
        print(f"Resotre list '{list_name}' to Todo section.")

    def doneTask(self, list_name: str, task_number: int) -> None:
        self.__moveTask(self.TodoLists, self.DoneLists, list_name, task_number)
        print(f"Done task {task_number} in list '{list_name}'.")

    def restoreTask(self, list_name: str, task_number: int) -> None:
        self.__moveTask(self.DoneLists, self.TodoLists, list_name, task_number)
        print(f"Restored task {task_number} in list '{list_name}' to Todo section.")

    def clearDoneList(self) -> None:
        opt = input("Are you sure to delete all the done tasks and done lists? (y/N): ")
        if opt.lower() == "y":
            self.DoneLists = {}
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
        list_name = self.__checkListName(list_name,no_create=True)
        print(f"\n## {list_name}\n")
        for i, task in enumerate(section[list_name], start=1):
            print(f"{i}. {task}")
        return

# ----------------------------------
# Visualize the todo lists and tasks
# ----------------------------------
    def viewTodo(self) -> None:
        print("# Todo")
        self.__viewSection(self.TodoLists)

    def viewTodoList(self, list_name: str) -> None:
        self.__viewList(self.TodoLists, list_name)

    def viewDone(self) -> None:
        print("# Done")
        self.__viewSection(self.DoneLists)

    def viewDoneList(self, list_name: str) -> None:
        self.__viewList(self.DoneLists, list_name)
        
    def viewAll(self) -> None:
        self.viewTodo()
        print("")
        self.viewDone()


# ----------------------
def main():
    DEBUG: bool = True
    # DEBUG:bool = False
    if DEBUG:
        HOME = Path(__file__).resolve().parent
    else:
        HOME = Path.home()

    TODO_FILE = HOME / "TODO.md"
    if DEBUG:
        tdmgr: TodoManager = TodoManager(TODO_FILE)
        tdmgr.viewAll()
        tdmgr.addList("Test List")
        tdmgr.addTask("Test List", "This is a test task")
        print("\n------\n")
        tdmgr.viewAll()

if __name__ == "__main__":
    main()
