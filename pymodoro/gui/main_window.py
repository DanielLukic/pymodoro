from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QCloseEvent, QIcon
from ..timer.states import TimerState
from ..timer.core import PomodoroTimer
from ..timer.controller import TimerController
from ..config.provider import ConfigProvider
from ..utils.logger import get_logger
from .styles import Fonts

class MainWindow(QMainWindow):
    def __init__(self, timer: PomodoroTimer, timer_controller: TimerController):
        super().__init__()
        self.timer = timer
        self.timer_controller = timer_controller
        self.config = ConfigProvider.get()
        self.logger = get_logger()
        self.tray_available = False
        self.setup_ui()
        self.connect_signals()
        self.update_display()
    
    def setup_ui(self):
        self.setWindowTitle("Pymodoro")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(Fonts.MAIN_TIMER)
        font.setBold(True)
        self.time_label.setFont(font)
        layout.addWidget(self.time_label)
        
        self.state_label = QLabel("Ready to start")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("color: gray;")
        layout.addWidget(self.state_label)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_clicked)
        self.start_button.setMinimumWidth(80)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_clicked)
        self.pause_button.setEnabled(False)
        self.pause_button.setMinimumWidth(80)
        button_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_clicked)
        self.reset_button.setMinimumWidth(80)
        button_layout.addWidget(self.reset_button)
        
        self.config_button = QPushButton("⚙")
        self.config_button.clicked.connect(self.show_configuration)
        self.config_button.setToolTip("Configuration")
        self.config_button.setMaximumWidth(30)
        button_layout.addWidget(self.config_button)
        
        layout.addLayout(button_layout)
        
        session_layout = QHBoxLayout()
        self.session_label = QLabel("Session: 1")
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_layout.addWidget(self.session_label)
        layout.addLayout(session_layout)
        
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        self.auto_restart_checkbox = QCheckBox("Auto-Start After Breaks")
        self.auto_restart_checkbox.setChecked(self.config.auto_start_work_after_break)
        self.auto_restart_checkbox.toggled.connect(self.toggle_auto_restart)
        settings_layout.addWidget(self.auto_restart_checkbox)
        
        layout.addWidget(settings_group)
        
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
    
    def connect_signals(self):
        self.timer.state_changed.connect(self.on_state_changed)
        self.timer.time_changed.connect(self.on_time_changed)
        self.timer.session_completed.connect(self.on_session_completed)
    
    def start_clicked(self):
        self.timer_controller.start_or_resume()
    
    def pause_clicked(self):
        self.timer_controller.pause_or_resume()
    
    def reset_clicked(self):
        self.timer_controller.reset()
    
    def show_configuration(self):
        from .settings import ConfigurationDialog
        dialog = ConfigurationDialog(self.config, self)
        if dialog.exec():
            self.auto_restart_checkbox.setChecked(self.config.auto_start_work_after_break)
    
    def toggle_auto_restart(self, checked):
        self.config.update_setting('auto_start_work_after_break', checked)
        self.logger.info(f"Auto-start after breaks {'enabled' if checked else 'disabled'}")
    
    @pyqtSlot(TimerState)
    def on_state_changed(self, state: TimerState):
        self.update_display()
    
    @pyqtSlot(int)
    def on_time_changed(self, remaining_seconds: int):
        self.time_label.setText(self.timer.get_time_display())
    
    @pyqtSlot(TimerState)
    def on_session_completed(self, completed_state: TimerState):
        if completed_state == TimerState.WORK:
            self.session_label.setText(f"Session: {self.timer.current_session}")
    
    def update_display(self):
        state = self.timer.current_state
        
        start_enabled, start_text = self.timer_controller.get_start_button_state()
        pause_enabled, pause_text = self.timer_controller.get_pause_button_state()
        
        self.start_button.setEnabled(start_enabled)
        self.start_button.setText(start_text)
        self.pause_button.setEnabled(pause_enabled)
        self.pause_button.setText(pause_text)
        
        if state == TimerState.IDLE:
            self.state_label.setText("Ready to start")
            work_duration = self.config.work_duration_seconds
            minutes = work_duration // 60
            seconds = work_duration % 60
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        elif state == TimerState.WORK:
            self.state_label.setText("Work Session")
        elif state == TimerState.SHORT_BREAK:
            self.state_label.setText("Short Break")
        elif state == TimerState.LONG_BREAK:
            self.state_label.setText("Long Break")
        elif state == TimerState.PAUSED:
            self.state_label.setText("Paused")
    
    def set_tray_available(self, available: bool):
        self.tray_available = available
    
    def closeEvent(self, event: QCloseEvent):
        if self.tray_available:
            event.ignore()
            self.hide()
        else:
            event.accept() 