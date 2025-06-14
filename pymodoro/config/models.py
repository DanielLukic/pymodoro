from pydantic import BaseModel, Field

class PomodoroConfig(BaseModel):
    work_duration: int = Field(default=25, ge=1, le=120)
    short_break_duration: int = Field(default=5, ge=1, le=60)
    long_break_duration: int = Field(default=15, ge=5, le=120)
    sessions_until_long_break: int = Field(default=4, ge=2, le=10)
    auto_start_work_after_break: bool = Field(default=True)
    enable_global_hotkey: bool = Field(default=False)
    global_hotkey: str = Field(default="ctrl+alt+space")
    
    # Audio settings
    enable_sounds: bool = Field(default=True)
    sound_volume: float = Field(default=0.7, ge=0.0, le=1.0)
    sound_type: str = Field(default="chimes")  # "chimes", "custom"
    work_start_sound: str = Field(default="")
    break_start_sound: str = Field(default="")
    session_complete_sound: str = Field(default="")
    timer_finish_sound: str = Field(default="")

    class Config:
        env_prefix = "PYMODORO_"

class AppState(BaseModel):
    current_session: int = Field(default=1)
    total_sessions_completed: int = Field(default=0)
    current_state: str = Field(default="IDLE") 