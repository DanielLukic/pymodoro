from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from .states import TimerState, TimerEvent
from ..config.provider import ConfigProvider

class PomodoroTimer(QObject):
    state_changed = pyqtSignal(TimerState)
    time_changed = pyqtSignal(int)
    session_completed = pyqtSignal(TimerState)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or ConfigProvider.get()
        self.current_state = TimerState.IDLE
        self.previous_state = TimerState.IDLE
        self.remaining_seconds = 0
        self.current_session = 1
        
        self.qt_timer = QTimer()
        self.qt_timer.timeout.connect(self._tick)
        self.qt_timer.setInterval(1000)
    
    def start_work_session(self, from_hotkey=False):
        if self.current_state != TimerState.IDLE:
            return
            
        self._change_state(TimerState.WORK)
        self.remaining_seconds = self.config.work_duration_seconds
        self._start_timer()
    
    def start_break(self):
        if self.current_state != TimerState.WORK:
            return
            
        completed_sessions = self.current_session - 1
        is_long_break = completed_sessions > 0 and completed_sessions % self.config.sessions_until_long_break == 0
        
        if is_long_break:
            self._change_state(TimerState.LONG_BREAK)
            self.remaining_seconds = self.config.long_break_duration_seconds
        else:
            self._change_state(TimerState.SHORT_BREAK)
            self.remaining_seconds = self.config.short_break_duration_seconds
        
        self._start_timer()
    
    def pause(self):
        if self.current_state in [TimerState.WORK, TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.qt_timer.stop()
            self.previous_state = self.current_state
            self._change_state(TimerState.PAUSED)
    
    def resume(self):
        if self.current_state == TimerState.PAUSED:
            self._change_state(self.previous_state)
            self._start_timer()
    
    def reset(self):
        self.qt_timer.stop()
        self._change_state(TimerState.IDLE)
        self.previous_state = TimerState.IDLE
        self.remaining_seconds = 0
        self.current_session = 1
    
    def _start_timer(self):
        self.qt_timer.start()
        self.time_changed.emit(self.remaining_seconds)
    
    def _tick(self):
        self.remaining_seconds -= 1
        self.time_changed.emit(self.remaining_seconds)
        
        if self.remaining_seconds <= 0:
            self._timer_finished()
    
    def _timer_finished(self):
        self.qt_timer.stop()
        current_state = self.current_state
        
        if current_state == TimerState.WORK:
            self.current_session += 1
            self.session_completed.emit(current_state)
            self.start_break()
        
        elif current_state in [TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self._change_state(TimerState.IDLE)
            self.session_completed.emit(current_state)
    
    def _change_state(self, new_state: TimerState):
        if new_state != self.current_state:
            self.current_state = new_state
            self.state_changed.emit(new_state)
    
    def get_time_display(self) -> str:
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}" 