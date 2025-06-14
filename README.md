# Pymodoro

A **production-ready** Linux-native Pomodoro timer with comprehensive desktop integration.

## ✨ Features

### **Core Timer**
- ⏰ Configurable work/break intervals (25min work, 5min/15min breaks by default)
- 🔄 Automatic session cycling with protected break time
- ⏸️ Pause/resume functionality with state persistence

### **Desktop Integration** 
- 🖥️ **System tray integration** with color-coded progress indicators
- 🖼️ **Semi-transparent break overlay** with countdown display
- ⌨️ **Global hotkey support** (optional, disabled by default)

### **Smart Auto-Start**
- 🖱️ **Auto-start work after breaks** - any mouse/keyboard activity triggers next session
- 🛡️ **Protected break time** - input during breaks doesn't interrupt them
- ⚙️ **Fully configurable** via GUI settings or system tray checkboxes

### **User Experience**
- 🎯 **Minimize to tray** - runs quietly in background
- 🔧 **Comprehensive settings dialog** - timer intervals, hotkeys, sound settings
- 📊 **Visual feedback** - tray icon shows current state and progress
- 🔊 **Sound alerts** - audio notifications for timer events with volume control
- 🧪 **Command line test mode** - for quick testing with custom intervals

## 🚀 Quick Start

### **Normal Mode**
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install PyQt6 pynput pydantic

# Run the application
python run.py
```

### **Test Mode** (for quick testing)
```bash
# 5 second work, 3 second break, 2 sessions until long break, 4 second long break
python run.py 5s 3s 2 4s

# 2 minute work, 30 second break
python run.py 2m 30s 2 1m
```

## 📋 System Requirements

- **OS**: Linux with desktop environment
- **Python**: 3.8+
- **Dependencies**: PyQt6, pynput, pydantic
- **System**: System tray support (available in most modern Linux DEs)

## 🎮 Usage

1. **Start timer**: Click "Start" in main window or tray menu
2. **Work session**: 25 minutes (or custom) of focused work
3. **Break time**: Automatic break with fullscreen overlay countdown
4. **Auto-restart**: Move mouse/type after break to start next session
5. **Configure**: Right-click tray icon → "Configuration..." or click ⚙ in main window

### **Keyboard Shortcuts**
- **Global hotkey**: `Ctrl+Alt+Space` (when enabled) - starts next pomodoro from anywhere
- **Break overlay**: `ESC` to dismiss overlay manually

### **System Tray**
- **Left click**: Show/hide main window
- **Right click**: Context menu with timer controls and settings
- **Icon colors**: Red (work), Teal (short break), Blue (long break), Yellow (paused)
- **Progress ring**: Visual countdown indicator

## ⚙️ Configuration

Settings are accessible via:
- **Main window**: Settings checkboxes + ⚙ configuration button
- **System tray**: Right-click menu checkboxes + "Configuration..."

### **Timer Settings**
- Work duration (1-120 minutes)
- Short break duration (1-60 minutes)
- Long break duration (5-120 minutes)  
- Sessions until long break (2-10)

### **Behavior Settings**
- Auto-start after breaks (enable/disable)
- Global hotkey (enable/disable + custom key combination)

### **Sound Settings**
- Enable/disable sound alerts
- Volume control (0-100%)
- Sound type selection (system sounds, custom files, none)
- Test buttons for each timer event

## 📂 File Locations

- **Config**: `~/.config/pymodoro/config.json`
- **Logs**: `~/.config/pymodoro/logs/`
- **State**: `~/.config/pymodoro/state.json`

## 🧪 Development & Testing

```bash
# Quick functional test (6 second cycle)
python run.py 6s 2s 2 3s

# Normal development setup
git clone <repository>
cd pymodoro
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## 📖 Documentation

- **[ROADMAP.md](ROADMAP.md)**: Detailed development plan and current status
- **Architecture**: Clean separation of timer logic, GUI, and system integration
- **Extensible**: Modular design for future enhancements

## 🔮 Current Status

**Phase 1-7: COMPLETE** ✅ - All core features implemented and working  
**Phase 8+: PLANNED** 📋 - Future enhancements and advanced features

## 🏆 Production Ready

The application is stable and ready for daily use with:
- ✅ Bug-free timer cycles 
- ✅ Reliable desktop integration
- ✅ Comprehensive error handling
- ✅ Persistent configuration
- ✅ Clean user experience

---

*Built with Python, PyQt6, and focus on Linux desktop integration.* 