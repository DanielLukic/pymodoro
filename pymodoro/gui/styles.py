"""
Centralized UI styling constants and utilities
Eliminates duplicated styling code across GUI components
"""

from PyQt6.QtGui import QColor

class Colors:
    """Color constants used throughout the application"""
    
    RED = QColor(220, 50, 47)
    TEAL = QColor(42, 161, 152) 
    BLUE = QColor(38, 139, 210)
    YELLOW = QColor(181, 137, 0)
    GRAY = QColor(128, 128, 128)
    WHITE = QColor(255, 255, 255)
    BLACK = QColor(0, 0, 0)
    GREEN = QColor(46, 125, 50)

class ButtonStyles:
    """Reusable button style templates"""
    
    @staticmethod
    def get_break_button_style(bg_color: str, border_color: str, hover_color: str, pressed_color: str) -> str:
        """Get consistent break overlay button styling"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px 24px;
                color: white;
                min-width: 120px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
            QPushButton:focus {{
                border: 3px solid rgba(255, 255, 255, 200);
            }}
        """
    
    @staticmethod
    def skip_button_style() -> str:
        """Red skip button style"""
        return ButtonStyles.get_break_button_style(
            "rgba(220, 50, 47, 180)",
            "rgba(220, 50, 47, 255)", 
            "rgba(220, 50, 47, 220)",
            "rgba(180, 40, 37, 255)"
        )
    
    @staticmethod
    def extend_button_style() -> str:
        """Blue extend button style"""
        return ButtonStyles.get_break_button_style(
            "rgba(38, 139, 210, 180)",
            "rgba(38, 139, 210, 255)",
            "rgba(38, 139, 210, 220)", 
            "rgba(30, 110, 180, 255)"
        )
    
    @staticmethod
    def pause_button_style() -> str:
        """Yellow pause button style"""
        return ButtonStyles.get_break_button_style(
            "rgba(181, 137, 0, 180)",
            "rgba(181, 137, 0, 255)",
            "rgba(181, 137, 0, 220)",
            "rgba(150, 110, 0, 255)"
        )

class StateColors:
    """Timer state color mappings"""
    
    WORK = Colors.RED
    SHORT_BREAK = Colors.TEAL
    LONG_BREAK = Colors.BLUE
    PAUSED = Colors.YELLOW
    IDLE = Colors.GRAY
    
    @staticmethod
    def get_color_for_state(state) -> QColor:
        """Get color for timer state"""
        from ..timer.states import TimerState
        
        color_map = {
            TimerState.WORK: StateColors.WORK,
            TimerState.SHORT_BREAK: StateColors.SHORT_BREAK,
            TimerState.LONG_BREAK: StateColors.LONG_BREAK,
            TimerState.PAUSED: StateColors.PAUSED,
            TimerState.IDLE: StateColors.IDLE
        }
        
        return color_map.get(state, StateColors.IDLE)

class Fonts:
    """Font size constants"""
    
    TIMER_LARGE = 72
    TITLE_LARGE = 48
    MAIN_TIMER = 32
    MESSAGE = 24
    BUTTON = 16
    SMALL = 14
    TINY = 10 