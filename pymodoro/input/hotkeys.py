from PyQt6.QtCore import QObject, pyqtSignal
from pynput import keyboard
import threading
from ..config.provider import ConfigProvider
from ..utils.logger import get_logger

class GlobalHotkeyManager(QObject):
    hotkey_triggered = pyqtSignal()
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or ConfigProvider.get()
        self.logger = get_logger()
        self.listener = None
        self.is_active = False
        
        # Start monitoring if enabled
        self.start_if_enabled()
    
    def start_if_enabled(self):
        # Clean API - no hasattr() checks!
        if self.config.enable_global_hotkey:
            self.start_monitoring()
    
    def start_monitoring(self):
        if self.is_active:
            return
            
        try:
            hotkey_combo = self.config.global_hotkey
            self.logger.info(f"Global hotkey enabled: {hotkey_combo}")
            
            # Parse hotkey combination
            keys = self._parse_hotkey(hotkey_combo)
            
            self.listener = keyboard.GlobalHotKeys({
                hotkey_combo: self._on_hotkey_pressed
            })
            
            self.listener.start()
            self.is_active = True
            self.logger.debug("Global hotkey monitoring active")
            
        except Exception as e:
            self.logger.error(f"Failed to register global hotkey: {e}")
            self.is_active = False
    
    def stop_monitoring(self):
        if self.listener and self.is_active:
            self.logger.debug("Stopping global hotkey monitoring")
            try:
                self.listener.stop()
            except:
                pass
            self.is_active = False
            self.logger.debug("Global hotkey monitoring stopped")
    
    def _parse_hotkey(self, hotkey_string):
        # Simple parsing for combinations like "ctrl+alt+space"
        parts = hotkey_string.lower().split('+')
        return parts
    
    def _on_hotkey_pressed(self):
        # Clean check for test mode using ConfigProvider
        if ConfigProvider.is_test_mode():
            self.logger.info("Global hotkey triggered (test mode)")
        else:
            self.logger.info("Global hotkey triggered")
        
        self.hotkey_triggered.emit()
    
    def update_hotkey(self, new_hotkey: str, enabled: bool):
        # Stop current monitoring
        self.stop_monitoring()
        
        # Update config would be handled by the caller
        
        # Restart if enabled
        if enabled:
            self.start_monitoring()
    
    def __del__(self):
        self.stop_monitoring() 