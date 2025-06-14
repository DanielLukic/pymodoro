import json
from pathlib import Path
from typing import Optional
from .models import PomodoroConfig, AppState

class ConfigManager:
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".config" / "pymodoro"
        
        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        self.state_file = config_dir / "state.json"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self.load_config()
        self.state = self.load_state()
    
    def load_config(self) -> PomodoroConfig:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return PomodoroConfig(**data)
            except (json.JSONDecodeError, ValueError):
                pass
        return PomodoroConfig()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config.model_dump(), f, indent=2)
    
    def load_state(self) -> AppState:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                return AppState(**data)
            except (json.JSONDecodeError, ValueError):
                pass
        return AppState()
    
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state.model_dump(), f, indent=2) 