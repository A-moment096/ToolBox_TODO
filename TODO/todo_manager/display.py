"""Display and formatting utilities for the todo manager."""

import subprocess
from typing import List
from rich import print as rprint
from rich.style import Style
from .types import Section


# Define custom styles
HEADING1_STYLE = Style(color="yellow", bold=True)
HEADING2_STYLE = Style(color="green", bold=True)
NUMBERED_STYLE = Style(color="cyan")


def print(*args, **kwargs):
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


def select_option(prompt: str, default: bool = True) -> bool:
    """Prompt the user for a yes/no answer."""
    while True:
        response = input(f"{prompt} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if response == '':
            return default
        elif response in ('y', 'yes'):
            return True
        elif response in ('n', 'no'):
            return False
        else:
            print("Invalid input, please enter 'y' or 'n'.")


class DisplayManager:
    """Handles output formatting and display of todo lists."""
    
    def __init__(self, viewer: str = ""):
        self.viewer = viewer
    
    def format_section(self, section: Section) -> str:
        """Format a section (todo or done) for display."""
        output = ""
        for list_name, tasks in section.items():
            output += f"\n## {list_name}\n"
            for i, task in enumerate(tasks, start=1):
                output += f"{i}. {task}\n"
        return output
    
    def format_list(self, section: Section, list_name: str) -> str:
        """Format a specific list for display."""
        output = f"\n## {list_name}\n"
        if list_name in section:
            for i, task in enumerate(section[list_name], start=1):
                output += f"{i}. {task}\n"
        else:
            output += "No tasks found in this list.\n"
        return output
    
    def display_output(self, output: str) -> None:
        """Output the content to the viewer or console."""
        if self.viewer:
            self._display_with_viewer(output)
        else:
            print(output)
    
    def _display_with_viewer(self, output: str) -> None:
        """Display output using the configured viewer."""
        command_list: List[str] = self.viewer.split()
        
        # Add viewer-specific options
        if self.viewer in ("bat", "batcat"):
            command_list.append("--language=markdown")
        elif self.viewer == "less":
            command_list.append("-R")
        elif self.viewer == "cat":
            command_list = ["cat"]
        
        try:
            process = subprocess.Popen(
                command_list,
                stdin=subprocess.PIPE,
                text=True,
            )
            process.communicate(input=output)
        except Exception as e:
            print(f"Failed to open viewer '{self.viewer}': {e}")
            # Fallback to console output
            print(output)
    
    def display_todo_section(self, todo_lists: Section) -> None:
        """Display the todo section."""
        output = "# Todo\n"
        output += self.format_section(todo_lists)
        self.display_output(output)
    
    def display_done_section(self, done_lists: Section) -> None:
        """Display the done section."""
        output = "# Done\n"
        output += self.format_section(done_lists)
        self.display_output(output)
    
    def display_all_sections(self, todo_lists: Section, done_lists: Section) -> None:
        """Display both todo and done sections."""
        output = "# Todo\n"
        output += self.format_section(todo_lists)
        output += "\n# Done\n"
        output += self.format_section(done_lists)
        self.display_output(output)
    
    def display_specific_list(self, section: Section, list_name: str, section_name: str = "") -> None:
        """Display a specific list from a section."""
        if section_name:
            output = f"# {section_name}\n"
        else:
            output = ""
        output += self.format_list(section, list_name)
        
        if list_name in section:
            self.display_output(output)
        else:
            print(f"No tasks found in the list '{list_name}'.")
    
    def set_viewer(self, viewer: str) -> None:
        """Set the viewer for output display."""
        self.viewer = viewer
