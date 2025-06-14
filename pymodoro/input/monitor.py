from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from pynput import mouse, keyboard
import threading
import time
from ..timer.states import TimerState
from ..config.provider import ConfigProvider
from ..utils.logger import get_logger

class InputMonitor(QObject):
    activity_detected = pyqtSignal()
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or ConfigProvider.get()
        self.logger = get_logger()
        self.is_monitoring = False
        self.mouse_listener = None
        self.keyboard_listener = None
        self.is_user_considered_idle = False
    
    def _create_fresh_listeners(self):
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except:
                pass
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except:
                pass
        
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_activity,
            on_click=self._on_mouse_activity,
            on_scroll=self._on_mouse_activity
        )
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_keyboard_activity,
            on_release=self._on_keyboard_activity
        )
    
    def start_monitoring(self, timer_state=None):
        if not self.config.auto_start_work_after_break:
            return
            
        # Only monitor when timer is IDLE (after breaks end)
        if timer_state != TimerState.IDLE:
            return
            
        if not self.is_monitoring:
            self.logger.info("Starting input monitoring for auto-start")
            self.is_monitoring = True
            self.is_user_considered_idle = True  # Assume idle after break
            
            try:
                self._create_fresh_listeners()
                self.mouse_listener.start()
                self.keyboard_listener.start()
                self.logger.debug("Input detection active - any activity will start next work session")
            except Exception as e:
                self.logger.error(f"Input monitoring failed: {e}")
                self.is_monitoring = False
    
    def stop_monitoring(self):
        if self.is_monitoring:
            self.logger.debug("Stopping input monitoring")
            self.is_monitoring = False
            self.is_user_considered_idle = False
            
            if self.mouse_listener:
                try:
                    self.mouse_listener.stop()
                except:
                    pass
            if self.keyboard_listener:
                try:
                    self.keyboard_listener.stop()
                except:
                    pass
            
            self.logger.debug("Input monitoring stopped")
    
    def _on_mouse_activity(self, *args):
        if self.is_monitoring:
            self._record_activity()
    
    def _on_keyboard_activity(self, *args):
        if self.is_monitoring:
            self._record_activity()
    
    def _record_activity(self):
        if self.is_user_considered_idle:
            if ConfigProvider.is_test_mode():
                self.logger.info("User returned! Auto-starting next work session (test mode)")
            else:
                self.logger.info("User activity detected - auto-starting work session")
            self.activity_detected.emit()
            self.stop_monitoring()  # Stop monitoring after triggering 