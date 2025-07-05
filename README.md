# Todo Manager

A simple file-based TODO manager, written in Python. It will create a `TODO.md` under your home folder, and create a `todo_config.toml` under your config folder: `$HOME/.config`. You can write your todo lists in `TODO.md` and use this simple tool to manage it.

By the way it is also the first tool in my tool box repository. Maybe there will be more, please check it.

## 📦 Installation

As a python module, it is recommended to install this tool under a virtual environment. You can easily install it use `pipx` or `uv tool`. But of course, you can freely install it with method you like. 

However, as this tool is *too simple* to be uploaded to package market place, if you want to try it, please download it from release and install it manually (still, should be really simple).

## 📋 Usage

### Basic Commands

> Information below is also shipped with help information. All these commands supports short form. 

```bash
# View all items
todo view

# View only todo items  
# Equivalent to `todo`
todo view --todo

# View only done items
todo view --done

# View specific list
todo view --list "My List"

# Add a task
todo add "Work" "Review pull requests"

# Add a new list
todo add-list "Shopping"

# Mark task as done
todo done "Work" 1

# Mark entire list as done  
todo done-list "Work"

# Restore completed task
todo restore "Work" 1

# Restore completed list
todo restore-list "Work"

# Reorder tasks
todo order "Work" 1 3

# Clear all done items
todo clear-done

# Edit file with configured editor
todo edit

# Save current state
todo save
```

### Configuration

```bash
# Set default editor
todo config --editor vim

# Set default file path
todo config --file ~/my-todos.md

# Set default viewer
todo config --viewer bat
```

### Debug Mode

Use `--debug` to work with files in the current directory instead of home directory:

```bash
todo --debug view
```

## 🔧 Configuration Files

The tool supports multiple configuration formats:

### JSON (`config.json`)
```json
{
    "editor": "vim",
    "file": "/path/to/TODO.md", 
    "viewer": "bat"
}
```

### YAML (`config.yaml`)
```yaml
editor: vim
file: /path/to/TODO.md
viewer: bat
```

### TOML (`config.toml`)
```toml
editor = "vim"
file = "/path/to/TODO.md"
viewer = "bat"
```

## ❓ Q&A

> Bug? Feature request? Contribute?

Issue and PR are welcome. Don't hesitate to let me know.

> Build it? Your environment setting?

Alright this project is actually really simple. It is a project for me to learn how a Python project is build and work. If you are an experienced developer, you must find it really simple, with a smell of AI coding. You are right.

Well, if you want to know how I configure my project, I use `uv` to replace `pip` and `venv`. To try this, you simply use `uv sync` command and, boom~, your develop environemnt is set up. But sorry I don't know how to set up environment with `pip` and `venv`. Guess it won't be very hard as everything is defined in `pyproject.toml`.