"""File I/O operations for the todo manager."""

import re
from pathlib import Path
from typing import List
from .types import Section
from .output import warning, success

TODO_SECTION = "Todo"
DONE_SECTION = "Done"


class FileIOManager:
    """Handles reading and writing markdown files for todo lists."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        
    def parse_file(self) -> tuple[Section, Section]:
        """Parse the markdown file and return todo and done sections."""
        todo_lists: Section = {}
        done_lists: Section = {}
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Todo file not found at {self.file_path}")
        
        file_lines: List[str] = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                file_lines.append(line.strip())

        current_section: Section = {}
        list_name = ""
        
        for line in file_lines:
            if not line:
                continue
                
            if line.startswith("# "):
                section_name = line[2:].strip()
                if section_name == TODO_SECTION:
                    current_section = todo_lists
                elif section_name == DONE_SECTION:
                    current_section = done_lists
                else:
                    warning(f"Unknown section: {section_name}")
                    continue
                    
            elif line.startswith("## "):
                list_name = line[3:].strip()
                current_section[list_name] = []
                
            else:
                # Parse numbered tasks or plain text
                line_match = re.match(r"^\d+\.\s(.*)$", line.strip())
                task: str = line_match.group(1) if line_match else line
                
                if list_name not in current_section:
                    warning(f"Warning: Task '{task}' found without a list.")
                    continue
                    
                current_section[list_name].append(task)
        
        return todo_lists, done_lists
    
    def write_file(self, todo_lists: Section, done_lists: Section) -> None:
        """Write the todo and done sections to the markdown file."""
        # Ensure the directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("# Todo\n\n")
            
            for list_name, tasks in todo_lists.items():
                f.write(f"## {list_name}\n\n")
                for i, task in enumerate(tasks, start=1):
                    f.write(f"{i}. {task}\n")
                f.write("\n")
            
            f.write("# Done\n\n")
            
            for list_name, tasks in done_lists.items():
                f.write(f"## {list_name}\n\n")
                for i, task in enumerate(tasks, start=1):
                    f.write(f"{i}. {task}\n")
                f.write("\n")
    
    def create_new_file(self) -> None:
        """Create a new todo file with basic structure."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("# Todo\n\n# Done\n")
        success(f"Created new todo file at {self.file_path}")
    
    def file_exists(self) -> bool:
        """Check if the todo file exists."""
        return self.file_path.exists()
