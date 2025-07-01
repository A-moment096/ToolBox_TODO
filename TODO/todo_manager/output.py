"""Output management for the todo manager."""

import re
import sys
from enum import Enum
from typing import Any, TextIO
from rich.console import Console
from rich.style import Style
from rich.text import Text


class OutputType(Enum):
    """Types of output messages."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DISPLAY = "display"


class OutputManager:
    """Manages different types of output with consistent formatting."""
    
    def __init__(self, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr):
        self.stdout = stdout
        self.stderr = stderr
        self.console = Console(file=stdout, force_terminal=True)
        self.error_console = Console(file=stderr, force_terminal=True)
        
        # Define styles for different output types
        self.bracket_styles = {
            OutputType.INFO: Style(color="blue", bold=True),
            OutputType.SUCCESS: Style(color="green", bold=True),
            OutputType.WARNING: Style(color="yellow", bold=True),
            OutputType.ERROR: Style(color="red", bold=True),
        }
        
        # Define styles for highlighting content within messages
        self.highlight_styles = {
            "number": Style(color="cyan", bold=True),
            "quoted": Style(color="magenta", bold=True),
            "default": Style(),
        }
        
        # Define styles for formatted content
        self.content_styles = {
            "heading1": Style(color="yellow", bold=True),
            "heading2": Style(color="green", bold=True),
            "numbered": Style(color="cyan"),
            "task": Style(color="white"),
        }
    
    def info(self, message: str) -> None:
        """Print an informational message."""
        self._print_message(message, OutputType.INFO)
    
    def success(self, message: str) -> None:
        """Print a success message."""
        self._print_message(message, OutputType.SUCCESS)
    
    def warning(self, message: str) -> None:
        """Print a warning message."""
        self._print_message(message, OutputType.WARNING)
    
    def error(self, message: str) -> None:
        """Print an error message to stderr."""
        self._print_message(message, OutputType.ERROR, use_stderr=True)
    
    def display(self, content: str) -> None:
        """Display formatted content with markdown-like styling."""
        lines = content.split('\n')
        for line in lines:
            self._print_styled_line(line)
    
    def _print_message(self, message: str, output_type: OutputType, use_stderr: bool = False) -> None:
        """Print a message with enhanced formatting for brackets and content highlights."""
        console = self.error_console if use_stderr else self.console
        
        if output_type == OutputType.DISPLAY:
            # For display content, use the existing styled line method
            self._print_styled_line(message)
            return
        
        # Create the bracket prefix with appropriate color
        bracket_style = self.bracket_styles.get(output_type, Style())
        prefix = f"[{output_type.value.upper()}]"
        
        # Create a rich Text object for the complete message
        text = Text()
        text.append(prefix, style=bracket_style)
        text.append(" ")
        
        # Highlight numbers and quoted text in the message content
        self._append_highlighted_text(text, message)
        
        console.print(text)
    
    def _append_highlighted_text(self, text: Text, message: str) -> None:
        """Append message text with highlighted numbers and quoted strings."""
        # Pattern to match numbers and quoted strings
        pattern = r"(\d+|'[^']*'|\"[^\"]*\")"
        
        last_end = 0
        for match in re.finditer(pattern, message):
            # Add text before the match (unhighlighted)
            before_text = message[last_end:match.start()]
            if before_text:
                text.append(before_text, style=self.highlight_styles["default"])
            
            # Add the matched content (highlighted)
            matched_text = match.group(1)
            if matched_text.isdigit():
                # Highlight numbers
                text.append(matched_text, style=self.highlight_styles["number"])
            else:
                # Highlight quoted strings
                text.append(matched_text, style=self.highlight_styles["quoted"])
            
            last_end = match.end()
        
        # Add any remaining text after the last match
        remaining_text = message[last_end:]
        if remaining_text:
            text.append(remaining_text, style=self.highlight_styles["default"])
    
    def _print_styled_line(self, line: str) -> None:
        """Print a line with appropriate styling based on content."""
        if line.startswith("# "):
            # Main heading
            text = Text(line, style=self.content_styles["heading1"])
        elif line.startswith("## "):
            # Sub heading
            text = Text(line, style=self.content_styles["heading2"])
        elif line and line[0].isdigit() and '. ' in line:
            # Numbered list item
            text = Text(line, style=self.content_styles["numbered"])
        else:
            # Regular text
            text = Text(line, style=self.content_styles["task"])
        
        self.console.print(text)
    
    def prompt(self, message: str, default: bool = True) -> bool:
        """Prompt the user for a yes/no answer."""
        while True:
            prompt_text = f"{message} [{'Y/n' if default else 'y/N'}]: "
            try:
                response = input(prompt_text).strip().lower()
                if response == '':
                    return default
                elif response in ('y', 'yes'):
                    return True
                elif response in ('n', 'no'):
                    return False
                else:
                    self.warning("Invalid input, please enter 'y' or 'n'.")
            except (KeyboardInterrupt, EOFError):
                self.info("\nOperation cancelled.")
                return False


# Global output manager instance
output_manager = OutputManager()

# Convenience functions for global use
def info(message: str) -> None:
    """Print an informational message."""
    output_manager.info(message)

def success(message: str) -> None:
    """Print a success message."""
    output_manager.success(message)

def warning(message: str) -> None:
    """Print a warning message."""
    output_manager.warning(message)

def error(message: str) -> None:
    """Print an error message."""
    output_manager.error(message)

def display(content: str) -> None:
    """Display formatted content."""
    output_manager.display(content)

def prompt(message: str, default: bool = True) -> bool:
    """Prompt the user for a yes/no answer."""
    return output_manager.prompt(message, default)
