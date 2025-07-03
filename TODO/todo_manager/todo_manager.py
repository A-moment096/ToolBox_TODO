"""Core TodoManager class for managing todo lists and tasks."""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from toml import load as toml_load
from rich import print as rich_print

from .config import ConfigManager
from .display import DisplayManager, select_option
from .file_io import FileIOManager
from .types import Section
from .output import info, success, warning, error


class TodoManager:
    """Main class for managing todo lists and tasks."""

    def __init__(
        self,
        todo_path: Path,
        config_path: Path = Path(),
        config_manager: Optional[ConfigManager] = None,
        file_manager: Optional[FileIOManager] = None,
        display_manager: Optional[DisplayManager] = None,
        viewer: str = "",
    ) -> None:
        self.file_path = todo_path
        self.config_path = config_path
        self.todo_lists: Section = {}
        self.done_lists: Section = {}

        # Use dependency injection or create defaults
        self.config_manager = config_manager or ConfigManager(config_path)
        self.file_manager = file_manager or FileIOManager(todo_path)
        self.display_manager = display_manager or DisplayManager()

        # Load configuration first
        if self.config_manager:
            self.config_manager.load_config(config_path)
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
            error(f"Todo file not found at {self.file_path}.")
            if select_option("Create a new todo file?"):
                info("Creating new todo file...")
                self.file_manager.create_new_file()
                self.todo_lists, self.done_lists = self.file_manager.parse_file()
            else:
                info("Exiting without creating a new todo file.")
                return

    def save_config(self, editor: str = "", file: str = "", viewer: str = "") -> None:
        """Save configuration settings."""
        if self.config_manager:
            self.config_manager.save_config(editor, file, viewer)
            # Update display manager if viewer changed
            if viewer:
                self.display_manager.set_viewer(viewer)
        else:
            error("No config manager available")

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
            info(f"Possible lists you'd like to refer to:")
            for i, name in enumerate(matched_names, 1):
                info(f"{i}. {name}")
            return matched_names
        else:
            warning(f"No matching list found.")
            return []

    def _check_list_name(self, list_name: str, no_create: bool = False) -> str:
        """Check if list exists, offer alternatives or creation."""
        if list_name in self.todo_lists:
            return list_name

        warning(f"No such list named as '{list_name}'.")
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
                    error("Invalid input: out of range")
                    return ""
            except ValueError:
                error("Invalid input, nothing changed.")
                return ""
        elif not no_create:
            if select_option(f"Create a new list named as '{list_name}'?"):
                return list_name
            else:
                info(f"No list created. Nothing changed")

        return ""

    def add_list(self, list_name: str, quiet: bool = False) -> None:
        """Add a new list if it doesn't exist."""
        if list_name in self.todo_lists:
            if not quiet:
                warning(f"List '{list_name}' already exists. No new list created.")
            return

        self.todo_lists[list_name] = []
        if not quiet:
            success(f"Added new list '{list_name}'.")

    def add_task(self, list_name: str, task: str) -> None:
        """Add a task to a list."""
        validated_list_name = self._check_list_name(list_name)
        if validated_list_name:
            self.add_list(validated_list_name, quiet=True)
            self.todo_lists[validated_list_name].append(task)
            success(f"Added task '{task}' to list '{validated_list_name}'.")
        else:
            info(f"Cancelled adding task, nothing changed")

    def order_task(self, list_name: str, old_position: int, new_position: int) -> None:
        """Reorder a task within a list."""
        validated_list_name = self._check_list_name(list_name, no_create=True)
        if not validated_list_name:
            return

        tasks = self.todo_lists[validated_list_name]

        if not self._validate_task_number(old_position, len(tasks)):
            error(f"Invalid task number {old_position} in list '{validated_list_name}'.")
            return

        if not self._validate_task_number(new_position, len(tasks)):
            error(
                f"Invalid new task number {new_position} in list '{validated_list_name}'."
            )
            return

        task = tasks.pop(old_position - 1)
        tasks.insert(new_position - 1, task)
        success(
            f"Moved task '{task}' from position {old_position} to {new_position} in list '{validated_list_name}'."
        )

    def _move_task(
        self, source: Section, target: Section, list_name: str, task_number: int
    ) -> bool:
        """Move a task between sections. Returns True if successful."""
        if list_name not in source:
            error(f"No such list named as {list_name}.")
            return False

        if not (1 <= task_number <= len(source[list_name])):
            error(f"Invalid task number {task_number} in list {list_name}.")
            return False

        task = source[list_name].pop(task_number - 1)

        if list_name in target:
            target[list_name].append(task)
        else:
            target[list_name] = [task]
        
        return True

    def _move_list(self, source: Section, target: Section, list_name: str) -> bool:
        """Move an entire list between sections. Returns True if successful."""
        if list_name not in source:
            error(f"No such list named as {list_name}.")
            return False

        target[list_name] = source.pop(list_name)
        return True

    def done_task(self, list_name: str, task_number: int) -> None:
        """Mark a task as done."""
        if self._move_task(self.todo_lists, self.done_lists, list_name, task_number):
            success(f"Done task {task_number} in list '{list_name}'.")

    def done_list(self, list_name: str) -> None:
        """Mark an entire list as done."""
        if self._move_list(self.todo_lists, self.done_lists, list_name):
            success(f"Done list '{list_name}'")

    def restore_task(self, list_name: str, task_number: int) -> None:
        """Restore a done task back to todo."""
        if self._move_task(self.done_lists, self.todo_lists, list_name, task_number):
            success(f"Restored task {task_number} in list '{list_name}' to Todo section.")

    def restore_list(self, list_name: str) -> None:
        """Restore a done list back to todo."""
        if self._move_list(self.done_lists, self.todo_lists, list_name):
            success(f"Restore list '{list_name}' to Todo section.")

    def clear_done_list(self, force: bool = False) -> None:
        """Clear all done tasks and lists."""
        if force:
            self.done_lists = {}
            success("Cleared all done tasks and lists.")
        else:
            if select_option(
                "Are you sure to delete all the done tasks and done lists?"
            ):
                self.done_lists = {}
                success("Cleared.")
            else:
                info("Abort. Done list not modified.")

    def edit_file(self, editor: str = "") -> None:
        """Open the todo file in the configured editor."""
        editor_to_use = editor or (
            self.config_manager.get_editor() if self.config_manager else ""
        )

        if not editor_to_use:
            error("No editor configured. Please set an editor using --editor option.")
            return

        if shutil.which(editor_to_use) is None:
            error(f"Editor '{editor_to_use}' not found in PATH.")
            return

        try:
            subprocess.run([editor_to_use, str(self.file_path)], check=True)
        except Exception as e:
            error(f"Failed to open editor: {e}")

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

    def _validate_task_number(self, task_number: int, list_size: int) -> bool:
        """Validate task number is within valid range."""
        return 1 <= task_number <= list_size

    def _validate_list_name(self, list_name: str) -> bool:
        """Validate list name is not empty and doesn't contain invalid characters."""
        return bool(list_name.strip()) and not any(char in list_name for char in ['#', '\n', '\r'])

    def self_intro(self) -> None:
        """Check the version of the Todo Manager."""
        try:
            with open(self.config_path, 'r') as f:
                config_data = toml_load(f)
                version = config_data.get('project', {}).get('version', 'unknown')
                author = config_data.get('project', {}).get('authors', [{}])[0].get('name', 'unknown')
                homepage = config_data.get('project', {}).get('urls').get('Homepage', 'unknown')
                rich_print(
f"""Todo Manager version {version}
This is a subproject of ToolBox, a collection of useful tools.
Author: {author}
Homepage: {homepage}""")
        except FileNotFoundError:
            error(f"Config file not found at {self.config_path}.")