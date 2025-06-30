"""Configuration management for the todo manager."""

import json
import toml
import yaml
from pathlib import Path
from typing import Dict, Optional


class ConfigManager:
    """Handles loading and saving configuration files in JSON, YAML, or TOML format."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.viewer: str = ""
        self.editor: str = ""
        self.file_path: Optional[Path] = None

        if config_path.exists():
            self.load_config(Path(config_path))
        else:
            print(f"Config file not found at {self.config_path}, using defaults.")
            self.viewer = ""
            self.editor = "vim"
            self.file_path = Path("")
        
    def load_config(self, default_file_path: Path) -> None:
        """Load configuration from the config file."""
        if not self.config_path.exists():
            print(f"Config file not found at {self.config_path}")
            return
            
        config_type = self.config_path.suffix
        
        try:
            with open(self.config_path, "r") as f:
                if config_type == ".json":
                    config_data: Dict = json.load(f)
                elif config_type in (".yml", ".yaml"):
                    config_data: Dict = yaml.safe_load(f)
                elif config_type == ".toml":
                    config_data = toml.load(f)
                else:
                    print(f"Unsupported config file type: {config_type}")
                    return
                    
                self.viewer = config_data.get("viewer", "")
                self.editor = config_data.get("editor", "")
                file_str = config_data.get("file", str(default_file_path))
                self.file_path = Path(file_str) if file_str else default_file_path
                
        except json.JSONDecodeError as e:
            print(f"Error loading JSON config: {e}")
        except yaml.YAMLError as e:
            print(f"Error loading YAML config: {e}")
        except toml.TomlDecodeError as e:
            print(f"Error loading TOML config: {e}")
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self, editor: str = "", file: str = "", viewer: str = "") -> None:
        """Save the current configuration to the config file."""
        config_data = {
            "editor": editor if editor else self.editor,
            "file": str(file) if file else str(self.file_path),
            "viewer": viewer if viewer else self.viewer
        }
        
        # Update internal state
        if editor:
            self.editor = editor
        if file:
            self.file_path = Path(file)
        if viewer:
            self.viewer = viewer
        
        config_type = self.config_path.suffix
        
        try:
            # Ensure the config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, "w") as f:
                if config_type == ".json":
                    json.dump(config_data, f, indent=4)
                elif config_type in (".yml", ".yaml"):
                    yaml.dump(config_data, f, default_flow_style=False)
                elif config_type == ".toml":
                    toml.dump(config_data, f)
                else:
                    print(f"Unsupported config file type: {config_type}")
                    return
                    
            print(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_file_path(self, default: Path) -> Path:
        """Get the configured file path or return default."""
        return self.file_path if self.file_path else default
    
    def get_editor(self) -> str:
        """Get the configured editor."""
        return self.editor
    
    def get_viewer(self) -> str:
        """Get the configured viewer.""" 
        return self.viewer
