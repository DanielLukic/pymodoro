import sys
import signal
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from .config.provider import ConfigProvider
from .timer.core import PomodoroTimer
from .timer.controller import TimerController
from .timer.states import TimerState
from .gui.main_window import MainWindow
from .gui.tray import SystemTray
from .gui.overlay import BreakOverlay
from .input.monitor import InputMonitor
from .input.hotkeys import GlobalHotkeyManager
from .audio.manager import AudioManager, SoundEvent
from .utils.logger import get_logger

class PyomodoroApp(QObject):
    quit_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.logger = get_logger()
        self.logger.info("Initializing Pymodoro application components")
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.config = ConfigProvider.get()
        self.logger.debug(f"Configuration loaded: {type(self.config).__name__}")
        
        self.timer = PomodoroTimer(self.config)
        self.timer_controller = TimerController(self.timer)
        self.logger.debug("Timer and controller initialized")
        
        self.main_window = MainWindow(self.timer, self.timer_controller)
        self.logger.debug("Main window created")
        
        self.system_tray = SystemTray(self.timer, self.timer_controller, self.main_window)
        self.logger.debug("System tray initialized")
        
        self.break_overlay = BreakOverlay(self.timer)
        self.logger.debug("Break overlay created")
        
        self.input_manager = InputMonitor(self.config)
        self.logger.debug("Input monitor initialized")
        
        self.audio_manager = AudioManager()
        self.audio_manager.set_enabled(self.config.enable_sounds)
        self.audio_manager.set_volume(self.config.sound_volume)
        self.logger.debug("Audio manager initialized")
        
        self.hotkey_manager = None
        if self.config.enable_global_hotkey:
            self._setup_global_hotkey()
        
        self._connect_signals()
        self._setup_signal_handlers()
        
        self.logger.info("Pymodoro application initialized successfully")
    
    def _setup_global_hotkey(self):
        try:
            self.hotkey_manager = GlobalHotkeyManager(self.config)
            self.hotkey_manager.hotkey_triggered.connect(self._on_global_hotkey)
            self.logger.info(f"Global hotkey enabled: {self.config.global_hotkey}")
        except Exception as e:
            self.logger.error(f"Failed to setup global hotkey: {e}")
            self.hotkey_manager = None
    
    def _connect_signals(self):
        self.quit_requested.connect(self.app.quit)
        
        self.input_manager.activity_detected.connect(self._on_user_activity)
        self.timer.state_changed.connect(self._on_timer_state_changed)
        self.timer.session_completed.connect(self._on_session_completed)
        self.logger.debug("Application signals connected")
    
    def _on_user_activity(self):
        if self.timer.current_state == TimerState.IDLE:
            self.logger.info("Auto-starting work session due to user activity")
            self.timer.start_work_session()
    
    def _on_timer_state_changed(self, state):
        self.logger.debug(f"Timer state changed to: {state.value}")
        
        # Handle input monitoring
        if state == TimerState.IDLE:
            self.input_manager.start_monitoring(state)
        else:
            self.input_manager.stop_monitoring()
        
        # Handle audio events
        if state == TimerState.WORK:
            self.audio_manager.play_sound(SoundEvent.WORK_START)
        elif state in [TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.audio_manager.play_sound(SoundEvent.BREAK_START)
    
    def _on_session_completed(self, completed_state):
        """Handle session completion audio"""
        self.logger.debug(f"Session completed: {completed_state.value}")
        
        if completed_state == TimerState.WORK:
            self.audio_manager.play_sound(SoundEvent.SESSION_COMPLETE)
        elif completed_state in [TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.audio_manager.play_sound(SoundEvent.TIMER_FINISH)
    
    def _cleanup_global_hotkey(self):
        if self.hotkey_manager:
            try:
                self.hotkey_manager.stop_monitoring()
                self.hotkey_manager = None
                self.logger.info("Global hotkey disabled")
            except Exception as e:
                self.logger.error(f"Error cleaning up global hotkey: {e}")
    
    def _on_global_hotkey(self):
        self.logger.info("Global hotkey triggered")
        self.timer.start_work_session(from_hotkey=True)
    
    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        self.logger.debug("Signal handlers configured")
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        self.quit()
    
    def run(self):
        try:
            self.logger.info("Starting Qt application event loop")
            return self.app.exec()
        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt received, shutting down")
            self.quit()
            return 0
    
    def quit(self):
        self.logger.info("Shutting down Pymodoro")
        
        if self.hotkey_manager:
            self._cleanup_global_hotkey()
        
        self.input_manager.stop_monitoring()
        
        if hasattr(self, 'audio_manager'):
            self.audio_manager.cleanup()
        
        self.quit_requested.emit() 