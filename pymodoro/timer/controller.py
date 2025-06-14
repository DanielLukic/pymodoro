from PyQt6.QtCore import QObject, pyqtSignal
from .core import PomodoroTimer
from .states import TimerState
from ..utils.logger import get_logger

class TimerController(QObject):
    """Centralized timer control logic - eliminates duplication across GUI components"""
    
    def __init__(self, timer: PomodoroTimer):
        super().__init__()
        self.timer = timer
        self.logger = get_logger()
    
    def start_or_resume(self):
        """Smart start/resume based on current state"""
        state = self.timer.current_state
        
        if state == TimerState.IDLE:
            self.logger.debug("Starting work session from controller")
            self.timer.start_work_session()
        elif state == TimerState.PAUSED:
            self.logger.debug("Resuming timer from controller")
            self.timer.resume()
        else:
            self.logger.warning(f"Cannot start/resume from state: {state}")
    
    def pause_or_resume(self):
        """Smart pause/resume based on current state"""
        state = self.timer.current_state
        
        if state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.logger.debug("Pausing timer from controller")
            self.timer.pause()
        elif state == TimerState.PAUSED:
            self.logger.debug("Resuming timer from controller")
            self.timer.resume()
        else:
            self.logger.warning(f"Cannot pause/resume from state: {state}")
    
    def reset(self):
        """Reset timer"""
        self.logger.debug("Resetting timer from controller")
        self.timer.reset()
    
    def get_start_button_state(self) -> tuple[bool, str]:
        """Get start button enabled state and text"""
        state = self.timer.current_state
        
        if state == TimerState.IDLE:
            return True, "Start"
        elif state == TimerState.PAUSED:
            return True, "Resume"
        else:
            return False, "Start"
    
    def get_pause_button_state(self) -> tuple[bool, str]:
        """Get pause button enabled state and text"""
        state = self.timer.current_state
        
        if state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            return True, "Pause"
        elif state == TimerState.PAUSED:
            return True, "Resume"
        else:
            return False, "Pause"
    
    def can_start(self) -> bool:
        """Check if timer can be started"""
        return self.timer.current_state in [TimerState.IDLE, TimerState.PAUSED]
    
    def can_pause(self) -> bool:
        """Check if timer can be paused"""
        return self.timer.current_state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK, TimerState.PAUSED]
    
    def is_running(self) -> bool:
        """Check if timer is actively running"""
        return self.timer.current_state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]
    
    def is_break_active(self) -> bool:
        """Check if a break is currently active"""
        return self.timer.current_state in [TimerState.SHORT_BREAK, TimerState.LONG_BREAK] 