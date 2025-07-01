"""Core TodoManager class for managing todo lists and tasks."""

import shutil
import subprocess
from pathlib import Path
from typing import List

from .config import ConfigManager
from .display import DisplayManager, select_option
from .file_io import FileIOManager
from .types import Section


class TodoManager:
    """Main class for managing todo lists and tasks."""

    def __init__(self, todo_path: Path = Path(), config_path: Path = Path(), viewer: str = "") -> None:
        self.file_path = todo_path
        self.config_path = config_path
        self.todo_lists: Section = {}
        self.done_lists: Section = {}

        # Initialize managers
        self.config_manager = ConfigManager(config_path)
        self.file_manager = FileIOManager(todo_path)
        self.display_manager = DisplayManager()

        # Load configuration first
        if self.config_manager:
            self.config_manager.load_config(todo_path)
            self.display_manager.set_viewer(self.config_manager.get_viewer())

        # Set the viewer for display manager if explicitly provided
        if viewer:
            self.display_manager.set_viewer(viewer)

        # Initialize file
        self._initialize_file()

    def _initialize_file(self) -> None:
        """Initialize the todo file, creating it if necessary."""
        try:
            self.todo_lists, self.done_lists = self.file_manager.parse_file()
        except FileNotFoundError:
            print(f"Todo file not found at {self.file_path}.")
            if select_option("Create a new todo file?"):
                print("Creating new todo file...")
                self.file_manager.create_new_file()
                self.todo_lists, self.done_lists = self.file_manager.parse_file()
            else:
                print("Exiting without creating a new todo file.")
                return

    def save_config(self, editor: str = "", file: str = "", viewer: str = "") -> None:
        """Save configuration settings."""
        if self.config_manager:
            self.config_manager.save_config(editor, file, viewer)
            # Update display manager if viewer changed
            if viewer:
                self.display_manager.set_viewer(viewer)
        else:
            print("No config manager available")

    def write_file(self) -> None:
        """Write current state to file."""
        self.file_manager.write_file(self.todo_lists, self.done_lists)

    def _match_list_name(self, list_name: str) -> List[str]:
        """Find matching list names."""
        matched_names: List[str] = []
        for existing_list in self.todo_lists:
            if list_name.lower() in existing_list.lower():
                matched_names.append(existing_list)

        if matched_names:
            print(f"Possible lists you'd like to refer to:")
            for i, name in enumerate(matched_names, 1):
                print(f"{i}. {name}")
            return matched_names
        else:
            print(f"No matching list found.")
            return []

    def _check_list_name(self, list_name: str, no_create: bool = False) -> str:
        """Check if list exists, offer alternatives or creation."""
        if list_name in self.todo_lists:
            return list_name

        print(f"No such list named as '{list_name}'.")
        matched_names = self._match_list_name(list_name)

        if matched_names:
            try:
                selection_text = input(
                    f"Use 0 for a new list '{list_name}', simple <Enter> to abort\nYour selection: "
                ).strip()

                if not selection_text:
                    return ""

                selection = int(selection_text)

                if selection == 0 and not no_create:
                    return list_name
                elif 1 <= selection <= len(matched_names):
                    return matched_names[selection - 1]
                else:
                    print("Invalid input: out of range")
                    return ""
            except ValueError:
                print("Invalid input, nothing changed.")
                return ""
        elif not no_create:
            if select_option(f"Create a new list named as '{list_name}'?"):
                return list_name
            else:
                print(f"No list created. Nothing changed")

        return ""

    def add_list(self, list_name: str, quiet: bool = False) -> None:
        """Add a new list if it doesn't exist."""
        if list_name in self.todo_lists:
            if not quiet:
                print(f"List '{list_name}' already exists. No new list created.")
            return

        self.todo_lists[list_name] = []
        if not quiet:
            print(f"Added new list '{list_name}'.")

    def add_task(self, list_name: str, task: str) -> None:
        """Add a task to a list."""
        validated_list_name = self._check_list_name(list_name)
        if validated_list_name:
            self.add_list(validated_list_name, quiet=True)
            self.todo_lists[validated_list_name].append(task)
            print(f"Added task '{task}' to list '{validated_list_name}'.")
        else:
            print(f"Cancelled adding task, nothing changed")

    def order_task(self, list_name: str, old_position: int, new_position: int) -> None:
        """Reorder a task within a list."""
        validated_list_name = self._check_list_name(list_name, no_create=True)
        if not validated_list_name:
            return

        tasks = self.todo_lists[validated_list_name]

        if not (1 <= old_position <= len(tasks)):
            print(f"Invalid task number {old_position} in list {validated_list_name}.")
            return

        if not (1 <= new_position <= len(tasks)):
            print(
                f"Invalid new task number {new_position} in list {validated_list_name}."
            )
            return

        task = tasks.pop(old_position - 1)
        tasks.insert(new_position - 1, task)
        print(
            f"Moved task '{task}' from position {old_position} to {new_position} in list '{validated_list_name}'."
        )

    def _move_task(
        self, source: Section, target: Section, list_name: str, task_number: int
    ) -> None:
        """Move a task between sections."""
        if list_name not in source:
            print(f"No such list named as {list_name}.")
            return

        if not (1 <= task_number <= len(source[list_name])):
            print(f"Invalid task number {task_number} in list {list_name}.")
            return

        task = source[list_name].pop(task_number - 1)

        if list_name in target:
            target[list_name].append(task)
        else:
            target[list_name] = [task]

    def _move_list(self, source: Section, target: Section, list_name: str) -> None:
        """Move an entire list between sections."""
        if list_name not in source:
            print(f"No such list named as {list_name}.")
            return

        target[list_name] = source.pop(list_name)

    def done_task(self, list_name: str, task_number: int) -> None:
        """Mark a task as done."""
        self._move_task(self.todo_lists, self.done_lists, list_name, task_number)
        print(f"Done task {task_number} in list '{list_name}'.")

    def done_list(self, list_name: str) -> None:
        """Mark an entire list as done."""
        self._move_list(self.todo_lists, self.done_lists, list_name)
        print(f"Done list '{list_name}'")

    def restore_task(self, list_name: str, task_number: int) -> None:
        """Restore a done task back to todo."""
        self._move_task(self.done_lists, self.todo_lists, list_name, task_number)
        print(f"Restored task {task_number} in list '{list_name}' to Todo section.")

    def restore_list(self, list_name: str) -> None:
        """Restore a done list back to todo."""
        self._move_list(self.done_lists, self.todo_lists, list_name)
        print(f"Restore list '{list_name}' to Todo section.")

    def clear_done_list(self, force: bool = False) -> None:
        """Clear all done tasks and lists."""
        if force:
            self.done_lists = {}
            print("Cleared all done tasks and lists.")
        else:
            if select_option(
                "Are you sure to delete all the done tasks and done lists?"
            ):
                self.done_lists = {}
                print("Cleared.")
            else:
                print("Abort. Done list not modified.")

    def edit_file(self, editor: str = "") -> None:
        """Open the todo file in the configured editor."""
        editor_to_use = editor or (
            self.config_manager.get_editor() if self.config_manager else ""
        )

        if not editor_to_use:
            print("No editor configured. Please set an editor using --editor option.")
            return

        if shutil.which(editor_to_use) is None:
            print(f"Editor '{editor_to_use}' not found in PATH.")
            return

        try:
            subprocess.run([editor_to_use, str(self.file_path)], check=True)
        except Exception as e:
            print(f"Failed to open editor: {e}")

    # View methods
    def view_todo(self) -> None:
        """Display the todo section."""
        self.display_manager.display_todo_section(self.todo_lists)

    def view_todo_list(self, list_name: str) -> None:
        """Display a specific todo list."""
        self.display_manager.display_specific_list(self.todo_lists, list_name, "Todo")

    def view_done(self) -> None:
        """Display the done section."""
        self.display_manager.display_done_section(self.done_lists)

    def view_done_list(self, list_name: str) -> None:
        """Display a specific done list."""
        self.display_manager.display_specific_list(self.done_lists, list_name, "Done")

    def view_all(self) -> None:
        """Display both todo and done sections."""
        self.display_manager.display_all_sections(self.todo_lists, self.done_lists)

    def has_list(self, list_name: str, section: str = "todo") -> bool:
        """Check if a list exists in the specified section."""
        if section == "todo":
            return list_name in self.todo_lists
        elif section == "done":
            return list_name in self.done_lists
        else:
            return list_name in self.todo_lists or list_name in self.done_lists
