from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import QObject, pyqtSlot, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont, QColor, QPen, QBrush
from ..timer.states import TimerState
from ..timer.core import PomodoroTimer
from ..timer.controller import TimerController
from ..config.provider import ConfigProvider
from ..utils.logger import get_logger
from .styles import StateColors

class SystemTray(QObject):
    def __init__(self, timer: PomodoroTimer, timer_controller: TimerController, main_window):
        super().__init__()
        self.timer = timer
        self.timer_controller = timer_controller
        self.main_window = main_window
        self.config = ConfigProvider.get()
        self.logger = get_logger()
        
        if not QSystemTrayIcon.isSystemTrayAvailable():
            raise Exception("System tray is not available")
        
        self.tray_icon = QSystemTrayIcon()
        self.setup_tray_icon()
        self.setup_context_menu()
        self.connect_signals()
        
        self.update_icon()
        self.tray_icon.show()
    
    def setup_tray_icon(self):
        self.tray_icon.setToolTip("Pymodoro - Ready")
        self.tray_icon.activated.connect(self.on_icon_activated)
    
    def setup_context_menu(self):
        self.context_menu = QMenu()
        
        self.show_action = self.context_menu.addAction("Show Window")
        self.show_action.triggered.connect(self.show_main_window)
        
        self.context_menu.addSeparator()
        
        self.start_action = self.context_menu.addAction("Start")
        self.start_action.triggered.connect(self.start_timer)
        
        self.pause_action = self.context_menu.addAction("Pause")
        self.pause_action.triggered.connect(self.pause_timer)
        self.pause_action.setEnabled(False)
        
        self.reset_action = self.context_menu.addAction("Reset")
        self.reset_action.triggered.connect(self.reset_timer)
        
        self.context_menu.addSeparator()
        
        self.auto_restart_action = self.context_menu.addAction("Auto-Start After Breaks")
        self.auto_restart_action.setCheckable(True)
        self.auto_restart_action.setChecked(self.config.auto_start_work_after_break)
        self.auto_restart_action.triggered.connect(self.toggle_auto_restart)
        
        self.context_menu.addSeparator()
        
        self.config_action = self.context_menu.addAction("Configuration...")
        self.config_action.triggered.connect(self.show_configuration)
        
        self.context_menu.addSeparator()
        
        self.quit_action = self.context_menu.addAction("Quit")
        self.quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(self.context_menu)
    
    def connect_signals(self):
        self.timer.state_changed.connect(self.on_state_changed)
        self.timer.time_changed.connect(self.on_time_changed)
    
    def create_timer_icon(self, text: str, color: QColor, progress: float = 0.0) -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(color)
        painter.setPen(color)
        painter.drawEllipse(2, 2, 60, 60)
        
        if progress > 0.0:
            painter.setPen(QColor(46, 125, 50))
            painter.setBrush(QColor(0, 0, 0, 0))
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            pen = painter.pen()
            border_width = int(64 * 0.15)
            pen.setWidth(border_width)
            painter.setPen(pen)
            
            margin = border_width // 2
            start_angle = 90 * 16
            span_angle = int(-progress * 360 * 16)
            painter.drawArc(margin, margin, 64 - 2*margin, 64 - 2*margin, start_angle, span_angle)
        
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        from PyQt6.QtCore import Qt
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        
        return QIcon(pixmap)
    
    def update_icon(self):
        state = self.timer.current_state
        time_text = self.timer.get_time_display()
        
        def get_rounded_minutes(remaining_seconds):
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            if seconds >= 30:
                minutes += 1
            return str(minutes)
        
        def get_progress(remaining_seconds, total_seconds):
            if total_seconds <= 0:
                return 0.0
            elapsed = total_seconds - remaining_seconds
            return elapsed / total_seconds
        
        if state == TimerState.IDLE:
            icon = self.create_timer_icon("●", StateColors.IDLE)
            tooltip = "Pymodoro - Ready"
        elif state == TimerState.WORK:
            total_seconds = self.config.work_duration_seconds
            progress = get_progress(self.timer.remaining_seconds, total_seconds)
            rounded_minutes = get_rounded_minutes(self.timer.remaining_seconds)
            icon = self.create_timer_icon(rounded_minutes, StateColors.WORK, progress)
            tooltip = f"Pymodoro - Work: {time_text}"
        elif state == TimerState.SHORT_BREAK:
            total_seconds = self.config.short_break_duration_seconds
            progress = get_progress(self.timer.remaining_seconds, total_seconds)
            rounded_minutes = get_rounded_minutes(self.timer.remaining_seconds)
            icon = self.create_timer_icon(rounded_minutes, StateColors.SHORT_BREAK, progress)
            tooltip = f"Pymodoro - Short Break: {time_text}"
        elif state == TimerState.LONG_BREAK:
            total_seconds = self.config.long_break_duration_seconds
            progress = get_progress(self.timer.remaining_seconds, total_seconds)
            rounded_minutes = get_rounded_minutes(self.timer.remaining_seconds)
            icon = self.create_timer_icon(rounded_minutes, StateColors.LONG_BREAK, progress)
            tooltip = f"Pymodoro - Long Break: {time_text}"
        elif state == TimerState.PAUSED:
            total_seconds = self.get_total_seconds_for_state(self.timer.previous_state)
            progress = get_progress(self.timer.remaining_seconds, total_seconds) if total_seconds > 0 else 0.0
            icon = self.create_timer_icon("||", StateColors.PAUSED, progress)
            tooltip = f"Pymodoro - Paused: {time_text}"
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(tooltip)
    
    def get_total_seconds_for_state(self, state):
        if state == TimerState.WORK:
            return self.config.work_duration_seconds
        elif state == TimerState.SHORT_BREAK:
            return self.config.short_break_duration_seconds
        elif state == TimerState.LONG_BREAK:
            return self.config.long_break_duration_seconds
        return 0
    
    def update_menu_state(self):
        start_enabled, start_text = self.timer_controller.get_start_button_state()
        pause_enabled, pause_text = self.timer_controller.get_pause_button_state()
        
        self.start_action.setEnabled(start_enabled)
        self.start_action.setText(start_text)
        self.pause_action.setEnabled(pause_enabled)
        self.pause_action.setText(pause_text)
    
    def on_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_main_window()
    
    def toggle_main_window(self):
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.show_main_window()
    
    def show_main_window(self):
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def start_timer(self):
        self.timer_controller.start_or_resume()
    
    def pause_timer(self):
        self.timer_controller.pause_or_resume()
    
    def reset_timer(self):
        self.timer_controller.reset()
    
    def quit_application(self):
        QApplication.quit()
    
    @pyqtSlot(TimerState)
    def on_state_changed(self, state: TimerState):
        self.update_icon()
        self.update_menu_state()
    
    @pyqtSlot(int)
    def on_time_changed(self, remaining_seconds: int):
        self.update_icon()
    
    def toggle_auto_restart(self, checked):
        self.config.update_setting('auto_start_work_after_break', checked)
        self.logger.info(f"Auto-start after breaks {'enabled' if checked else 'disabled'}")
    
    def show_configuration(self):
        from .settings import ConfigurationDialog
        dialog = ConfigurationDialog(self.config, self.main_window)
        if dialog.exec():
            self.auto_restart_action.setChecked(self.config.auto_start_work_after_break) 