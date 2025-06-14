import os
import subprocess
from pathlib import Path
from typing import Optional, Dict
from enum import Enum
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ..config.provider import ConfigProvider
from ..utils.logger import get_logger
from .tones import ToneGenerator

class SoundEvent(Enum):
    """Timer events that can trigger sounds"""
    WORK_START = "work_start"
    BREAK_START = "break_start" 
    SESSION_COMPLETE = "session_complete"
    TIMER_FINISH = "timer_finish"

class SoundType(Enum):
    """Types of sounds available"""
    CHIMES = "chimes"
    CUSTOM = "custom"

class AudioPlaybackThread(QThread):
    """Background thread for playing audio without blocking UI"""
    
    def __init__(self, sound_path: str, volume: float = 1.0):
        super().__init__()
        self.sound_path = sound_path
        self.volume = volume
        self.logger = get_logger()
    
    def run(self):
        """Play sound in background thread"""
        try:
            self._play_file_sound(self.sound_path)
        except Exception as e:
            self.logger.error(f"Audio playback failed: {e}")
    
    def _play_file_sound(self, file_path: str):
        """Play sound file using available audio players"""
        if not os.path.exists(file_path):
            self.logger.error(f"Sound file not found: {file_path}")
            return
            
        try:
            subprocess.run(['paplay', file_path], check=False, capture_output=True)
        except FileNotFoundError:
            try:
                subprocess.run(['aplay', file_path], check=False, capture_output=True)
            except FileNotFoundError:
                try:
                    subprocess.run(['ffplay', '-nodisp', '-autoexit', file_path], 
                                 check=False, capture_output=True)
                except FileNotFoundError:
                    self.logger.error("No audio player available (tried paplay, aplay, ffplay)")

class AudioManager(QObject):
    """Manages audio playback for timer events"""
    
    def __init__(self):
        super().__init__()
        self.config = ConfigProvider.get()
        self.logger = get_logger()
        self.enabled = self.config.enable_sounds
        self.volume = self.config.sound_volume
        self.sound_type = SoundType.CHIMES if self.config.sound_type == "chimes" else SoundType.CUSTOM
        
        self.tone_generator = ToneGenerator()
        self.chime_sounds = {}
        self.sound_mappings: Dict[SoundEvent, str] = {}
        
        self.active_threads = []
        self._setup_sounds()
    
    def _setup_sounds(self):
        """Setup sound mappings based on current configuration"""
        if self.sound_type == SoundType.CHIMES:
            self._setup_chime_sounds()
        else:
            self._setup_custom_sounds()
    
    def _setup_chime_sounds(self):
        """Setup generated chime sounds"""
        try:
            self.chime_sounds = self.tone_generator.create_chime_sounds()
            self.sound_mappings = {
                SoundEvent.WORK_START: self.chime_sounds['work_start'],
                SoundEvent.BREAK_START: self.chime_sounds['break_start'],
                SoundEvent.SESSION_COMPLETE: self.chime_sounds['session_complete'],
                SoundEvent.TIMER_FINISH: self.chime_sounds['timer_finish']
            }
            self.logger.info("Generated chime sounds successfully")
        except Exception as e:
            self.logger.error(f"Failed to generate chime sounds: {e}")
            self.enabled = False
    
    def _setup_custom_sounds(self):
        """Setup custom sound file mappings"""
        self.sound_mappings = {
            SoundEvent.WORK_START: self.config.work_start_sound,
            SoundEvent.BREAK_START: self.config.break_start_sound,
            SoundEvent.SESSION_COMPLETE: self.config.session_complete_sound,
            SoundEvent.TIMER_FINISH: self.config.timer_finish_sound
        }
        
        # Check if custom files exist
        missing_files = []
        for event, file_path in self.sound_mappings.items():
            if file_path and not Path(file_path).exists():
                missing_files.append(f"{event.value}: {file_path}")
        
        if missing_files:
            self.logger.warning(f"Custom sound files not found: {missing_files}")
        
        self.logger.info("Custom sound mappings configured")
    
    def play_sound(self, event: SoundEvent):
        """Play sound for timer event"""
        if not self.enabled:
            return
            
        sound_path = self.sound_mappings.get(event)
        if not sound_path:
            self.logger.debug(f"No sound configured for event: {event.value}")
            return
        
        # For custom sounds, check if file exists
        if self.sound_type == SoundType.CUSTOM and not Path(sound_path).exists():
            self.logger.warning(f"Sound file not found: {sound_path}")
            return
            
        self.logger.debug(f"Playing sound for event: {event.value}")
        
        thread = AudioPlaybackThread(sound_path, self.volume)
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        self.active_threads.append(thread)
        thread.start()
    
    def _cleanup_thread(self, thread: AudioPlaybackThread):
        """Clean up finished audio thread"""
        if thread in self.active_threads:
            self.active_threads.remove(thread)
    
    def set_enabled(self, enabled: bool):
        """Enable/disable audio"""
        self.enabled = enabled
        self.logger.info(f"Audio {'enabled' if enabled else 'disabled'}")
    
    def set_volume(self, volume: float):
        """Set audio volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        self.logger.debug(f"Audio volume set to {self.volume:.1%}")
    
    def set_sound_type(self, sound_type: SoundType):
        """Set sound type (chimes/custom)"""
        self.sound_type = sound_type
        self._setup_sounds()
        self.logger.info(f"Sound type set to: {sound_type.value}")
    
    def set_custom_sound(self, event: SoundEvent, file_path: str):
        """Set custom sound file for event"""
        if Path(file_path).exists():
            self.sound_mappings[event] = file_path
            self.logger.info(f"Custom sound set for {event.value}: {file_path}")
        else:
            self.logger.error(f"Sound file not found: {file_path}")
    
    def test_sound(self, event: SoundEvent):
        """Test play a sound"""
        self.logger.info(f"Testing sound for event: {event.value}")
        self.play_sound(event)
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        for thread in self.active_threads[:]:
            if thread.isRunning():
                thread.terminate()
                thread.wait(1000)
            self._cleanup_thread(thread)
        self.logger.debug("All sounds stopped")
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_all_sounds()
        if hasattr(self, 'tone_generator'):
            self.tone_generator.cleanup() 