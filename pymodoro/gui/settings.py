import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QSpinBox, QPushButton, QCheckBox, QGroupBox,
                             QDialogButtonBox, QTabWidget, QWidget, QLineEdit,
                             QSlider, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..utils.logger import get_logger
from ..audio.manager import SoundEvent

class ConfigurationDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logger = get_logger()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        self.setWindowTitle("Pymodoro Configuration")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Timer settings tab
        timer_tab = QWidget()
        timer_layout = QVBoxLayout(timer_tab)
        
        # Timer durations group
        durations_group = QGroupBox("Timer Durations")
        durations_layout = QGridLayout(durations_group)
        
        # Work duration
        durations_layout.addWidget(QLabel("Work Duration:"), 0, 0)
        self.work_duration_spin = QSpinBox()
        self.work_duration_spin.setRange(1, 120)
        self.work_duration_spin.setSuffix(" min")
        durations_layout.addWidget(self.work_duration_spin, 0, 1)
        
        # Short break duration
        durations_layout.addWidget(QLabel("Short Break:"), 1, 0)
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 60)
        self.short_break_spin.setSuffix(" min")
        durations_layout.addWidget(self.short_break_spin, 1, 1)
        
        # Long break duration
        durations_layout.addWidget(QLabel("Long Break:"), 2, 0)
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(5, 120)
        self.long_break_spin.setSuffix(" min")
        durations_layout.addWidget(self.long_break_spin, 2, 1)
        
        # Sessions until long break
        durations_layout.addWidget(QLabel("Sessions until Long Break:"), 3, 0)
        self.sessions_spin = QSpinBox()
        self.sessions_spin.setRange(2, 10)
        durations_layout.addWidget(self.sessions_spin, 3, 1)
        
        timer_layout.addWidget(durations_group)
        

        timer_layout.addStretch()
        
        tabs.addTab(timer_tab, "Timer")
        
        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        # Notifications group
        notifications_group = QGroupBox("Behavior Settings")
        notifications_group_layout = QVBoxLayout(notifications_group)
        
        self.auto_restart_cb = QCheckBox("Auto-start work after breaks end")
        notifications_group_layout.addWidget(self.auto_restart_cb)
        
        notifications_layout.addWidget(notifications_group)
        
        # Hotkey group
        hotkey_group = QGroupBox("Global Hotkey Settings")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        self.hotkey_enabled_cb = QCheckBox("Enable global hotkey to start next pomodoro")
        hotkey_layout.addWidget(self.hotkey_enabled_cb)
        
        hotkey_input_layout = QHBoxLayout()
        hotkey_input_layout.addWidget(QLabel("Hotkey combination:"))
        
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("e.g., ctrl+alt+p")
        hotkey_input_layout.addWidget(self.hotkey_input)
        
        self.hotkey_test_btn = QPushButton("Test")
        self.hotkey_test_btn.clicked.connect(self.test_hotkey)
        hotkey_input_layout.addWidget(self.hotkey_test_btn)
        
        hotkey_layout.addLayout(hotkey_input_layout)
        
        hotkey_help = QLabel("Use combinations like: ctrl+alt+p, ctrl+shift+s, etc.\nPress the hotkey anywhere to start the next pomodoro session.")
        hotkey_help.setStyleSheet("color: gray; font-size: 10px;")
        hotkey_help.setWordWrap(True)
        hotkey_layout.addWidget(hotkey_help)
        
        notifications_layout.addWidget(hotkey_group)
        

        notifications_layout.addStretch()
        
        tabs.addTab(notifications_tab, "Misc")
        
        # Sound settings tab
        sound_tab = QWidget()
        sound_layout = QVBoxLayout(sound_tab)
        
        # Main sound controls
        main_sound_group = QGroupBox("Sound Alerts")
        main_sound_layout = QVBoxLayout(main_sound_group)
        
        self.enable_sounds_cb = QCheckBox("Enable sound alerts")
        main_sound_layout.addWidget(self.enable_sounds_cb)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(25)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setMinimumWidth(40)
        volume_layout.addWidget(self.volume_label)
        
        main_sound_layout.addLayout(volume_layout)
        sound_layout.addWidget(main_sound_group)
        
        # Sound type selection
        type_group = QGroupBox("Sound Type")
        type_layout = QVBoxLayout(type_group)
        
        self.sound_type_combo = QComboBox()
        self.sound_type_combo.addItems(["Chimes", "Custom sounds"])
        type_layout.addWidget(self.sound_type_combo)
        
        sound_layout.addWidget(type_group)
        
        # Sound events configuration
        events_group = QGroupBox("Sound Events")
        events_layout = QGridLayout(events_group)
        
        # Headers
        events_layout.addWidget(QLabel("Event"), 0, 0)
        events_layout.addWidget(QLabel("Sound File"), 0, 1)
        events_layout.addWidget(QLabel("Actions"), 0, 2)
        
        # Work start
        events_layout.addWidget(QLabel("Work starts:"), 1, 0)
        self.work_sound_label = QLabel("Built-in chime")
        self.work_sound_label.setStyleSheet("color: gray; font-style: italic;")
        events_layout.addWidget(self.work_sound_label, 1, 1)
        
        work_actions = QHBoxLayout()
        self.work_browse_btn = QPushButton("Browse...")
        self.work_browse_btn.clicked.connect(lambda: self.browse_sound_file(SoundEvent.WORK_START))
        self.work_test_btn = QPushButton("Test")
        self.work_test_btn.clicked.connect(lambda: self.test_sound(SoundEvent.WORK_START))
        work_actions.addWidget(self.work_browse_btn)
        work_actions.addWidget(self.work_test_btn)
        work_widget = QWidget()
        work_widget.setLayout(work_actions)
        events_layout.addWidget(work_widget, 1, 2)
        
        # Break start
        events_layout.addWidget(QLabel("Break starts:"), 2, 0)
        self.break_sound_label = QLabel("Built-in chime")
        self.break_sound_label.setStyleSheet("color: gray; font-style: italic;")
        events_layout.addWidget(self.break_sound_label, 2, 1)
        
        break_actions = QHBoxLayout()
        self.break_browse_btn = QPushButton("Browse...")
        self.break_browse_btn.clicked.connect(lambda: self.browse_sound_file(SoundEvent.BREAK_START))
        self.break_test_btn = QPushButton("Test")
        self.break_test_btn.clicked.connect(lambda: self.test_sound(SoundEvent.BREAK_START))
        break_actions.addWidget(self.break_browse_btn)
        break_actions.addWidget(self.break_test_btn)
        break_widget = QWidget()
        break_widget.setLayout(break_actions)
        events_layout.addWidget(break_widget, 2, 2)
        
        # Session complete
        events_layout.addWidget(QLabel("Session complete:"), 3, 0)
        self.session_sound_label = QLabel("Built-in chime")
        self.session_sound_label.setStyleSheet("color: gray; font-style: italic;")
        events_layout.addWidget(self.session_sound_label, 3, 1)
        
        session_actions = QHBoxLayout()
        self.session_browse_btn = QPushButton("Browse...")
        self.session_browse_btn.clicked.connect(lambda: self.browse_sound_file(SoundEvent.SESSION_COMPLETE))
        self.session_test_btn = QPushButton("Test")
        self.session_test_btn.clicked.connect(lambda: self.test_sound(SoundEvent.SESSION_COMPLETE))
        session_actions.addWidget(self.session_browse_btn)
        session_actions.addWidget(self.session_test_btn)
        session_widget = QWidget()
        session_widget.setLayout(session_actions)
        events_layout.addWidget(session_widget, 3, 2)
        
        # Timer finish
        events_layout.addWidget(QLabel("Timer finish:"), 4, 0)
        self.finish_sound_label = QLabel("Built-in chime")
        self.finish_sound_label.setStyleSheet("color: gray; font-style: italic;")
        events_layout.addWidget(self.finish_sound_label, 4, 1)
        
        finish_actions = QHBoxLayout()
        self.finish_browse_btn = QPushButton("Browse...")
        self.finish_browse_btn.clicked.connect(lambda: self.browse_sound_file(SoundEvent.TIMER_FINISH))
        self.finish_test_btn = QPushButton("Test")
        self.finish_test_btn.clicked.connect(lambda: self.test_sound(SoundEvent.TIMER_FINISH))
        finish_actions.addWidget(self.finish_browse_btn)
        finish_actions.addWidget(self.finish_test_btn)
        finish_widget = QWidget()
        finish_widget.setLayout(finish_actions)
        events_layout.addWidget(finish_widget, 4, 2)
        
        sound_layout.addWidget(events_group)
        sound_layout.addStretch()
        
        tabs.addTab(sound_tab, "Sounds")
        
        layout.addWidget(tabs)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self.save_and_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        
        layout.addWidget(button_box)
    
    def load_settings(self):
        # Load current settings into the UI
        self.work_duration_spin.setValue(self.config.work_duration)
        self.short_break_spin.setValue(self.config.short_break_duration)
        self.long_break_spin.setValue(self.config.long_break_duration)
        self.sessions_spin.setValue(self.config.sessions_until_long_break)
        
        self.auto_restart_cb.setChecked(self.config.auto_start_work_after_break)
        
        self.hotkey_enabled_cb.setChecked(self.config.enable_global_hotkey)
        self.hotkey_input.setText(self.config.global_hotkey)
        
        # Load sound settings
        self.enable_sounds_cb.setChecked(self.config.enable_sounds)
        self.volume_slider.setValue(int(self.config.sound_volume * 100))
        self._update_volume_label(int(self.config.sound_volume * 100))
        
        # Set sound type combo
        sound_type_map = {"chimes": 0, "custom": 1}
        self.sound_type_combo.setCurrentIndex(sound_type_map.get(self.config.sound_type, 0))
        
        # Load custom sound file paths
        self._update_sound_labels()
        
        # Connect sound settings signals
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        self.enable_sounds_cb.toggled.connect(self._on_sounds_toggled)
        self.sound_type_combo.currentTextChanged.connect(self._on_sound_type_changed)
    
    def save_and_accept(self):
        # Save settings to config
        self.config.work_duration = self.work_duration_spin.value()
        self.config.short_break_duration = self.short_break_spin.value()
        self.config.long_break_duration = self.long_break_spin.value()
        self.config.sessions_until_long_break = self.sessions_spin.value()
        
        self.config.auto_start_work_after_break = self.auto_restart_cb.isChecked()
        
        self.config.enable_global_hotkey = self.hotkey_enabled_cb.isChecked()
        self.config.global_hotkey = self.hotkey_input.text().strip()
        
        # Save sound settings
        self.config.enable_sounds = self.enable_sounds_cb.isChecked()
        self.config.sound_volume = self.volume_slider.value() / 100.0
        
        sound_type_map = {0: "chimes", 1: "custom"}
        self.config.sound_type = sound_type_map.get(self.sound_type_combo.currentIndex(), "chimes")
        
        # Save to file
        from ..config.manager import ConfigManager
        config_manager = ConfigManager()
        config_manager.save_config()
        
        self.logger.info("Configuration saved")
        self.accept()
    
    def restore_defaults(self):
        from ..config.models import PomodoroConfig
        defaults = PomodoroConfig()
        
        self.work_duration_spin.setValue(defaults.work_duration)
        self.short_break_spin.setValue(defaults.short_break_duration)
        self.long_break_spin.setValue(defaults.long_break_duration)
        self.sessions_spin.setValue(defaults.sessions_until_long_break)
        
        self.auto_restart_cb.setChecked(defaults.auto_start_work_after_break)
        
        self.hotkey_enabled_cb.setChecked(defaults.enable_global_hotkey)
        self.hotkey_input.setText(defaults.global_hotkey)
        
        # Restore sound defaults
        self.enable_sounds_cb.setChecked(defaults.enable_sounds)
        self.volume_slider.setValue(int(defaults.sound_volume * 100))
        self._update_volume_label(int(defaults.sound_volume * 100))
        
        sound_type_map = {"chimes": 0, "custom": 1}
        self.sound_type_combo.setCurrentIndex(sound_type_map.get(defaults.sound_type, 0))
        
        # Clear custom sound paths
        self.config.work_start_sound = ""
        self.config.break_start_sound = ""
        self.config.session_complete_sound = ""
        self.config.timer_finish_sound = ""
        self._update_sound_labels()
    
    def test_hotkey(self):
        hotkey_str = self.hotkey_input.text().strip()
        if not hotkey_str:
            self.show_message("Please enter a hotkey combination")
            return
        
        from ..input.hotkeys import GlobalHotkeyManager
        if GlobalHotkeyManager.validate_hotkey_string(hotkey_str):
            self.show_message(f"✓ Valid hotkey: {hotkey_str}")
        else:
            self.show_message(f"✗ Invalid hotkey format: {hotkey_str}\nExample: ctrl+alt+p")
    
    def show_message(self, message):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Hotkey Test")
        msg.setText(message)
        msg.exec()
    
    def _update_volume_label(self, value):
        """Update volume percentage label"""
        self.volume_label.setText(f"{value}%")
    
    def _on_sounds_toggled(self, enabled):
        """Handle sound enable/disable"""
        self.volume_slider.setEnabled(enabled)
        self.sound_type_combo.setEnabled(enabled)
        
        # Enable/disable all sound controls
        self.work_browse_btn.setEnabled(enabled)
        self.work_test_btn.setEnabled(enabled)
        self.break_browse_btn.setEnabled(enabled)
        self.break_test_btn.setEnabled(enabled)
        self.session_browse_btn.setEnabled(enabled)
        self.session_test_btn.setEnabled(enabled)
        self.finish_browse_btn.setEnabled(enabled)
        self.finish_test_btn.setEnabled(enabled)
    
    def _on_sound_type_changed(self, text):
        """Handle sound type change"""
        is_custom = text == "Custom sounds"
        
        # Enable/disable browse buttons based on sound type
        self.work_browse_btn.setEnabled(is_custom and self.enable_sounds_cb.isChecked())
        self.break_browse_btn.setEnabled(is_custom and self.enable_sounds_cb.isChecked())
        self.session_browse_btn.setEnabled(is_custom and self.enable_sounds_cb.isChecked())
        self.finish_browse_btn.setEnabled(is_custom and self.enable_sounds_cb.isChecked())
        
        self._update_sound_labels()
    
    def _update_sound_labels(self):
        """Update sound file labels based on current settings"""
        is_custom = self.sound_type_combo.currentText() == "Custom sounds"
        
        if is_custom:
            self.work_sound_label.setText(self._get_sound_file_display(self.config.work_start_sound))
            self.break_sound_label.setText(self._get_sound_file_display(self.config.break_start_sound))
            self.session_sound_label.setText(self._get_sound_file_display(self.config.session_complete_sound))
            self.finish_sound_label.setText(self._get_sound_file_display(self.config.timer_finish_sound))
        else:
            self.work_sound_label.setText("Built-in chime")
            self.break_sound_label.setText("Built-in chime")
            self.session_sound_label.setText("Built-in chime")
            self.finish_sound_label.setText("Built-in chime")
    
    def _get_sound_file_display(self, file_path: str) -> str:
        """Get display text for sound file path"""
        if not file_path:
            return "No file selected"
        return os.path.basename(file_path)
    
    def browse_sound_file(self, event: SoundEvent):
        """Browse for custom sound file"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle(f"Select sound for {event.value.replace('_', ' ').title()}")
        file_dialog.setNameFilter("Audio files (*.wav *.mp3 *.ogg *.flac);;All files (*)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
            
            # Update config based on event type
            if event == SoundEvent.WORK_START:
                self.config.work_start_sound = selected_file
            elif event == SoundEvent.BREAK_START:
                self.config.break_start_sound = selected_file
            elif event == SoundEvent.SESSION_COMPLETE:
                self.config.session_complete_sound = selected_file
            elif event == SoundEvent.TIMER_FINISH:
                self.config.timer_finish_sound = selected_file
            
            self._update_sound_labels()
            self.logger.info(f"Selected sound file for {event.value}: {selected_file}")
    
    def test_sound(self, event: SoundEvent):
        """Test play a sound event"""
        try:
            from ..audio.manager import AudioManager
            audio_manager = AudioManager()
            audio_manager.set_enabled(True)
            audio_manager.set_volume(self.volume_slider.value() / 100.0)
            audio_manager.test_sound(event)
            self.logger.debug(f"Testing sound for event: {event.value}")
        except Exception as e:
            self.logger.error(f"Failed to test sound: {e}")
            self.show_message(f"Sound test failed: {str(e)}") 