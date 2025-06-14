from enum import Enum

class TimerState(Enum):
    IDLE = "idle"
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"

class TimerEvent(Enum):
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    RESET = "reset"
    TICK = "tick"
    FINISH = "finish" 