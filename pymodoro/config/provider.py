"""
ConfigProvider - Singleton pattern for unified configuration access

Eliminates all hasattr() checks by providing a clean, consistent API
regardless of whether we're in normal mode or test mode.
"""

from abc import ABC, abstractmethod
from typing import Optional
import json
from pathlib import Path
from .models import PomodoroConfig
from .manager import ConfigManager


class BaseConfig(ABC):
    """Base configuration interface - provides consistent API for all config types"""
    
    @property
    @abstractmethod
    def work_duration_seconds(self) -> int:
        """Work session duration in seconds"""
        pass
    
    @property
    @abstractmethod
    def short_break_duration_seconds(self) -> int:
        """Short break duration in seconds"""
        pass
    
    @property
    @abstractmethod
    def long_break_duration_seconds(self) -> int:
        """Long break duration in seconds"""
        pass
    
    @property
    @abstractmethod
    def work_duration(self) -> int:
        """Work session duration in minutes (for display)"""
        pass
    
    @property
    @abstractmethod
    def short_break_duration(self) -> int:
        """Short break duration in minutes (for display)"""
        pass
    
    @property
    @abstractmethod
    def long_break_duration(self) -> int:
        """Long break duration in minutes (for display)"""
        pass
    
    @property
    @abstractmethod
    def sessions_until_long_break(self) -> int:
        pass
    
    @property
    @abstractmethod
    def auto_start_work_after_break(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def enable_global_hotkey(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def global_hotkey(self) -> str:
        pass
    
    @property
    @abstractmethod
    def enable_sounds(self) -> bool:
        pass
    
    @property
    @abstractmethod
    def sound_volume(self) -> float:
        pass
    
    @property
    @abstractmethod
    def sound_type(self) -> str:
        pass
    
    @property
    @abstractmethod
    def work_start_sound(self) -> str:
        pass
    
    @property
    @abstractmethod
    def break_start_sound(self) -> str:
        pass
    
    @property
    @abstractmethod
    def session_complete_sound(self) -> str:
        pass
    
    @property
    @abstractmethod
    def timer_finish_sound(self) -> str:
        pass
    
    @abstractmethod
    def update_setting(self, key: str, value) -> None:
        """Update a setting and persist if necessary"""
        pass


class PersistentConfig(BaseConfig):
    """Production config - loads from file and persists changes"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".config" / "pymodoro"
        
        self.config_dir = config_dir
        self.config_file = config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
    
    def _load_config(self) -> PomodoroConfig:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return PomodoroConfig(**data)
            except (json.JSONDecodeError, ValueError):
                pass
        return PomodoroConfig()
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config.model_dump(), f, indent=2)
    
    @property
    def work_duration_seconds(self) -> int:
        return self.config.work_duration * 60
    
    @property
    def short_break_duration_seconds(self) -> int:
        return self.config.short_break_duration * 60
    
    @property
    def long_break_duration_seconds(self) -> int:
        return self.config.long_break_duration * 60
    
    @property
    def work_duration(self) -> int:
        return self.config.work_duration
    
    @work_duration.setter
    def work_duration(self, value: int) -> None:
        self.config.work_duration = value
    
    @property
    def short_break_duration(self) -> int:
        return self.config.short_break_duration
    
    @short_break_duration.setter
    def short_break_duration(self, value: int) -> None:
        self.config.short_break_duration = value
    
    @property
    def long_break_duration(self) -> int:
        return self.config.long_break_duration
    
    @long_break_duration.setter
    def long_break_duration(self, value: int) -> None:
        self.config.long_break_duration = value
    
    @property
    def sessions_until_long_break(self) -> int:
        return self.config.sessions_until_long_break
    
    @sessions_until_long_break.setter
    def sessions_until_long_break(self, value: int) -> None:
        self.config.sessions_until_long_break = value
    
    @property
    def auto_start_work_after_break(self) -> bool:
        return self.config.auto_start_work_after_break
    
    @auto_start_work_after_break.setter
    def auto_start_work_after_break(self, value: bool) -> None:
        self.config.auto_start_work_after_break = value
    
    @property
    def enable_global_hotkey(self) -> bool:
        return self.config.enable_global_hotkey
    
    @enable_global_hotkey.setter
    def enable_global_hotkey(self, value: bool) -> None:
        self.config.enable_global_hotkey = value
    
    @property
    def global_hotkey(self) -> str:
        return self.config.global_hotkey
    
    @global_hotkey.setter
    def global_hotkey(self, value: str) -> None:
        self.config.global_hotkey = value
    
    @property
    def enable_sounds(self) -> bool:
        return self.config.enable_sounds
    
    @enable_sounds.setter
    def enable_sounds(self, value: bool) -> None:
        self.config.enable_sounds = value
    
    @property
    def sound_volume(self) -> float:
        return self.config.sound_volume
    
    @sound_volume.setter
    def sound_volume(self, value: float) -> None:
        self.config.sound_volume = value
    
    @property
    def sound_type(self) -> str:
        return self.config.sound_type
    
    @sound_type.setter
    def sound_type(self, value: str) -> None:
        self.config.sound_type = value
    
    @property
    def work_start_sound(self) -> str:
        return self.config.work_start_sound
    
    @work_start_sound.setter
    def work_start_sound(self, value: str) -> None:
        self.config.work_start_sound = value
    
    @property
    def break_start_sound(self) -> str:
        return self.config.break_start_sound
    
    @break_start_sound.setter
    def break_start_sound(self, value: str) -> None:
        self.config.break_start_sound = value
    
    @property
    def session_complete_sound(self) -> str:
        return self.config.session_complete_sound
    
    @session_complete_sound.setter
    def session_complete_sound(self, value: str) -> None:
        self.config.session_complete_sound = value
    
    @property
    def timer_finish_sound(self) -> str:
        return self.config.timer_finish_sound
    
    @timer_finish_sound.setter
    def timer_finish_sound(self, value: str) -> None:
        self.config.timer_finish_sound = value
    
    def update_setting(self, key: str, value) -> None:
        """Update a setting and save to file"""
        setattr(self.config, key, value)
        self.config_manager.save_config()
    
    def get_raw_config(self) -> PomodoroConfig:
        """Get the underlying Pydantic config for compatibility"""
        return self.config


class InMemoryConfig(BaseConfig):
    """Test config - uses provided values, no persistence"""
    
    def __init__(self, test_values: dict):
        # Set up defaults first
        base_config = PomodoroConfig()
        
        # Override with test values
        self._work_seconds = test_values.get('_work_seconds', base_config.work_duration * 60)
        self._short_break_seconds = test_values.get('_short_break_seconds', base_config.short_break_duration * 60)
        self._long_break_seconds = test_values.get('_long_break_seconds', base_config.long_break_duration * 60)
        
        self._sessions_until_long_break = test_values.get('sessions_until_long_break', base_config.sessions_until_long_break)
        self._auto_start_work_after_break = test_values.get('auto_start_work_after_break', base_config.auto_start_work_after_break)
        self._enable_global_hotkey = test_values.get('enable_global_hotkey', base_config.enable_global_hotkey)
        self._global_hotkey = test_values.get('global_hotkey', base_config.global_hotkey)
        
        # Audio settings
        self._enable_sounds = test_values.get('enable_sounds', base_config.enable_sounds)
        self._sound_volume = test_values.get('sound_volume', base_config.sound_volume)
        self._sound_type = test_values.get('sound_type', base_config.sound_type)
        self._work_start_sound = test_values.get('work_start_sound', base_config.work_start_sound)
        self._break_start_sound = test_values.get('break_start_sound', base_config.break_start_sound)
        self._session_complete_sound = test_values.get('session_complete_sound', base_config.session_complete_sound)
        self._timer_finish_sound = test_values.get('timer_finish_sound', base_config.timer_finish_sound)
    
    @property
    def work_duration_seconds(self) -> int:
        return self._work_seconds
    
    @property
    def short_break_duration_seconds(self) -> int:
        return self._short_break_seconds
    
    @property
    def long_break_duration_seconds(self) -> int:
        return self._long_break_seconds
    
    @property
    def work_duration(self) -> int:
        return max(1, self._work_seconds // 60)
    
    @work_duration.setter
    def work_duration(self, value: int) -> None:
        self._work_seconds = value * 60
    
    @property
    def short_break_duration(self) -> int:
        return max(1, self._short_break_seconds // 60)
    
    @short_break_duration.setter
    def short_break_duration(self, value: int) -> None:
        self._short_break_seconds = value * 60
    
    @property
    def long_break_duration(self) -> int:
        return max(1, self._long_break_seconds // 60)
    
    @long_break_duration.setter
    def long_break_duration(self, value: int) -> None:
        self._long_break_seconds = value * 60
    
    @property
    def sessions_until_long_break(self) -> int:
        return self._sessions_until_long_break
    
    @sessions_until_long_break.setter
    def sessions_until_long_break(self, value: int) -> None:
        self._sessions_until_long_break = value
    
    @property
    def auto_start_work_after_break(self) -> bool:
        return self._auto_start_work_after_break
    
    @auto_start_work_after_break.setter
    def auto_start_work_after_break(self, value: bool) -> None:
        self._auto_start_work_after_break = value
    
    @property
    def enable_global_hotkey(self) -> bool:
        return self._enable_global_hotkey
    
    @enable_global_hotkey.setter
    def enable_global_hotkey(self, value: bool) -> None:
        self._enable_global_hotkey = value
    
    @property
    def global_hotkey(self) -> str:
        return self._global_hotkey
    
    @global_hotkey.setter
    def global_hotkey(self, value: str) -> None:
        self._global_hotkey = value
    
    @property
    def enable_sounds(self) -> bool:
        return self._enable_sounds
    
    @enable_sounds.setter
    def enable_sounds(self, value: bool) -> None:
        self._enable_sounds = value
    
    @property
    def sound_volume(self) -> float:
        return self._sound_volume
    
    @sound_volume.setter
    def sound_volume(self, value: float) -> None:
        self._sound_volume = value
    
    @property
    def sound_type(self) -> str:
        return self._sound_type
    
    @sound_type.setter
    def sound_type(self, value: str) -> None:
        self._sound_type = value
    
    @property
    def work_start_sound(self) -> str:
        return self._work_start_sound
    
    @work_start_sound.setter
    def work_start_sound(self, value: str) -> None:
        self._work_start_sound = value
    
    @property
    def break_start_sound(self) -> str:
        return self._break_start_sound
    
    @break_start_sound.setter
    def break_start_sound(self, value: str) -> None:
        self._break_start_sound = value
    
    @property
    def session_complete_sound(self) -> str:
        return self._session_complete_sound
    
    @session_complete_sound.setter
    def session_complete_sound(self, value: str) -> None:
        self._session_complete_sound = value
    
    @property
    def timer_finish_sound(self) -> str:
        return self._timer_finish_sound
    
    @timer_finish_sound.setter
    def timer_finish_sound(self, value: str) -> None:
        self._timer_finish_sound = value
    
    def update_setting(self, key: str, value) -> None:
        """Update in-memory setting (no persistence in test mode)"""
        setattr(self, f'_{key}', value)


class ConfigProvider:
    """Singleton config provider - single access point for all configuration"""
    
    _instance: Optional['ConfigProvider'] = None
    _config: Optional[BaseConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, config: BaseConfig) -> None:
        """Initialize the provider with a specific config implementation"""
        instance = cls()
        instance._config = config
    
    @classmethod
    def get(cls) -> BaseConfig:
        """Get the current config instance"""
        instance = cls()
        if instance._config is None:
            # Default to persistent config if not initialized
            instance._config = PersistentConfig()
        return instance._config
    
    @classmethod
    def is_test_mode(cls) -> bool:
        """Check if we're running in test mode"""
        instance = cls()
        return isinstance(instance._config, InMemoryConfig)
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)"""
        cls._instance = None
        cls._config = None 