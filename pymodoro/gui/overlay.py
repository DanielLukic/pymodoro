from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QKeyEvent
from ..timer.states import TimerState
from ..timer.core import PomodoroTimer
from ..utils.logger import get_logger
from .styles import ButtonStyles, Fonts

class BreakOverlay(QWidget):
    def __init__(self, timer: PomodoroTimer):
        super().__init__()
        self.timer = timer
        self.logger = get_logger()
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.setStyleSheet("""
            BreakOverlay {
                background-color: black;
            }
            QLabel, QPushButton {
                background-color: transparent;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        self.break_title = QLabel()
        title_font = QFont()
        title_font.setPointSize(Fonts.TITLE_LARGE)
        title_font.setBold(True)
        self.break_title.setFont(title_font)
        self.break_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.break_title)
        
        self.time_label = QLabel("05:00")
        time_font = QFont()
        time_font.setPointSize(Fonts.TIMER_LARGE)
        time_font.setBold(True)
        self.time_label.setFont(time_font)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        self.message_label = QLabel("Take a break and relax")
        message_font = QFont()
        message_font.setPointSize(Fonts.MESSAGE)
        self.message_label.setFont(message_font)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: rgba(255, 255, 255, 180);")
        layout.addWidget(self.message_label)
        
        layout.addSpacing(50)
        
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(20)
        
        self.skip_button = QPushButton("Skip Break")
        self.skip_button.setFont(QFont("", Fonts.BUTTON))
        self.skip_button.setStyleSheet(ButtonStyles.skip_button_style())
        self.skip_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.skip_button.clicked.connect(self.skip_break)
        button_layout.addWidget(self.skip_button)
        
        self.extend_button = QPushButton("Extend Break")
        self.extend_button.setFont(QFont("", Fonts.BUTTON))
        self.extend_button.setStyleSheet(ButtonStyles.extend_button_style())
        self.extend_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.extend_button.clicked.connect(self.extend_break)
        button_layout.addWidget(self.extend_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.setFont(QFont("", Fonts.BUTTON))
        self.pause_button.setStyleSheet(ButtonStyles.pause_button_style())
        self.pause_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.pause_button.clicked.connect(self.pause_break)
        button_layout.addWidget(self.pause_button)
        
        layout.addLayout(button_layout)
        
        layout.addSpacing(30)
        
        self.dismiss_label = QLabel("Press ESC to dismiss")
        dismiss_font = QFont()
        dismiss_font.setPointSize(Fonts.SMALL)
        self.dismiss_label.setFont(dismiss_font)
        self.dismiss_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dismiss_label.setStyleSheet("color: rgba(255, 255, 255, 120);")
        layout.addWidget(self.dismiss_label)
    
    def connect_signals(self):
        self.timer.state_changed.connect(self.on_state_changed)
        self.timer.time_changed.connect(self.on_time_changed)
    
    def show_overlay(self):
        screens = self.screen().availableGeometry()
        self.setGeometry(screens)
        self.update_display()
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self.skip_button.setFocus()
        self.logger.debug("Break overlay shown with focus set")
    
    def hide_overlay(self):
        self.logger.debug("Break overlay hidden")
        self.hide()
    
    def update_display(self):
        state = self.timer.current_state
        time_display = self.timer.get_time_display()
        
        if state == TimerState.SHORT_BREAK:
            self.break_title.setText("Short Break")
            self.break_title.setStyleSheet("color: rgba(42, 161, 152, 255);")
            self.message_label.setText("Take a quick breather")
        elif state == TimerState.LONG_BREAK:
            self.break_title.setText("Long Break")
            self.break_title.setStyleSheet("color: rgba(38, 139, 210, 255);")
            self.message_label.setText("Time for a longer rest")
        elif state == TimerState.PAUSED:
            if self.timer.previous_state == TimerState.SHORT_BREAK:
                self.break_title.setText("Short Break - Paused")
                self.break_title.setStyleSheet("color: rgba(181, 137, 0, 255);")
            elif self.timer.previous_state == TimerState.LONG_BREAK:
                self.break_title.setText("Long Break - Paused")
                self.break_title.setStyleSheet("color: rgba(181, 137, 0, 255);")
            self.message_label.setText("Break paused")
            self.pause_button.setText("Resume")
        else:
            self.hide_overlay()
            return
        
        self.time_label.setText(time_display)
        
        if state != TimerState.PAUSED:
            self.pause_button.setText("Pause")
    
    def skip_break(self):
        self.logger.info("Break skipped by user")
        self.timer.reset()
        self.hide_overlay()
    
    def extend_break(self):
        extension_seconds = 300
        self.timer.remaining_seconds += extension_seconds
        self.logger.info(f"Break extended by {extension_seconds // 60} minutes")
        self.timer.time_changed.emit(self.timer.remaining_seconds)
    
    def pause_break(self):
        if self.timer.current_state == TimerState.PAUSED:
            self.logger.info("Break resumed by user")
        else:
            self.logger.info("Break paused by user")
        
        from ..timer.controller import TimerController
        controller = TimerController(self.timer)
        controller.pause_or_resume()
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.logger.debug("ESC pressed - dismissing break overlay")
            self.hide_overlay()
            event.accept()
            return
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)
    
    @pyqtSlot(TimerState)
    def on_state_changed(self, state: TimerState):
        if state in [TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.show_overlay()
        elif state == TimerState.PAUSED and self.timer.previous_state in [TimerState.SHORT_BREAK, TimerState.LONG_BREAK]:
            self.update_display()
        else:
            self.hide_overlay()
    
    @pyqtSlot(int)
    def on_time_changed(self, remaining_seconds: int):
        if self.isVisible():
            self.update_display() 