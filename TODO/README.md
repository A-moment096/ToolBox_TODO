# Todo CLI Manager

A command-line todo list manager with rich formatting and comprehensive features.

## Features

- ✅ **Organized Lists**: Create and manage multiple todo lists
- ✅ **Rich Formatting**: Beautiful colored output with rich library
- ✅ **Task Management**: Add, complete, restore, and reorder tasks
- ✅ **List Operations**: Create, complete, and restore entire lists
- ✅ **File-based Storage**: Uses markdown format for easy editing
- ✅ **Smart Matching**: Fuzzy matching for list names
- ✅ **Done Section**: Separate completed tasks and lists

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x todo.py
```

## Usage Examples

```bash
# View all items
python todo.py view

# Add a task
python todo.py add "Work" "Review pull requests"

# Mark task as done
python todo.py done "Work" 1

# Create new list
python todo.py add-list "Shopping"

# Use debug mode (current directory)
python todo.py --debug view
```
