# Pymodoro - Linux Pomodoro App Roadmap

## Project Overview

A Linux-native Pomodoro timer that integrates seamlessly with the desktop environment, featuring:
- System tray integration with timer display
- GUI window for configuration and controls  
- Semi-transparent fullscreen break overlay with countdown
- Auto-start work sessions after breaks (configurable)
- Single persistent desktop notification (no clutter!)
- Global hotkey support for instant timer start
- Configurable pomodoro and break intervals

## Complexity Assessment: **Medium → Low** ✅

Much more manageable in Python due to mature Linux desktop integration libraries.
**Status**: Production-ready with all core features implemented.

## Technology Stack

### Core Components & Libraries

#### **1. GUI Framework: PyQt6** ✅
- **Library**: `PyQt6`
- **Complexity**: Low-Medium
- Native system tray, transparency, overlay windows built-in

#### **2. Input Detection** ✅
- **Library**: `pynput`
- **Complexity**: Low
- Mature, well-documented global input monitoring

#### **3. Break Overlay Window** ✅
- **Technology**: PyQt6 fullscreen window with transparency
- **Complexity**: Low-Medium
- Built-in support for always-on-top, transparency

#### **4. Configuration Management** ✅
- **Library**: `pydantic` + JSON
- **Complexity**: Very Low
- Type-safe configuration with validation

#### **5. System Integration** ✅
- **Notifications**: `plyer` with single persistent notification
- **Desktop**: Native Linux desktop integration
- **Complexity**: Low

## Development Phases

### **Phase 1: Core Timer + Basic GUI** ✅ (COMPLETE)
- [x] Timer state machine implementation
- [x] Basic PyQt6 window with start/stop/reset controls
- [x] Configuration loading/saving system
- [x] Basic timer display

**Deliverables:**
- Working timer logic ✅
- Functional GUI window ✅
- Configuration file handling ✅

### **Phase 2: System Tray Integration** ✅ (COMPLETE)
- [x] System tray icon implementation
- [x] Context menu with timer controls
- [x] Timer display in tray tooltip/icon
- [x] Minimize to tray functionality
- [x] Show/hide main window
- [x] Color-coded tray icons with progress indicators

**Deliverables:**
- Fully functional system tray ✅
- Timer status visible in tray ✅

### **Phase 3: Break Overlay** ✅ (COMPLETE)
- [x] Fullscreen semi-transparent overlay window
- [x] Break countdown display
- [x] Proper window management (always-on-top)
- [x] Cross-desktop compatibility testing
- [x] Overlay dismiss handling

**Deliverables:**
- Working break overlay ✅
- Countdown timer display ✅
- Proper transparency and positioning ✅

### **Phase 4: Auto-Start After Breaks** ✅ (COMPLETE)
- [x] Global input monitoring with `pynput`
- [x] Auto-start work session after breaks end (configurable)
- [x] Integration with timer state machine 
- [x] Proper cleanup and resource management
- [x] Breaks are protected - input during breaks does NOT interrupt them

**Deliverables:**
- Automatic work session start after breaks complete ✅
- Configurable auto-start behavior ✅
- Sacred break time - no accidental interruptions ✅

### **Phase 5: Polish & Features** ✅ (COMPLETE)
- [x] Desktop notifications for timer events
- [x] Error handling and logging
- [x] Application startup/shutdown handling
- [x] Resource cleanup
- [x] Settings persistence and validation
- [x] Configuration interface with system tray checkboxes
- [x] Configuration interface with main window checkboxes  
- [x] Full configuration dialog with timer settings
- [x] Single updating notification system (no more clutter!)
- [x] Global hotkey support (configurable, disabled by default)
- [x] Fixed notification clutter and crashes
- [x] Fixed all AttributeError issues in timer core and config dialog

**Deliverables:**
- Production-ready application ✅
- Comprehensive error handling ✅
- Single persistent notification with real-time updates ✅
- Global hotkey for instant pomodoro start ✅
- Persistent logging to ~/.config/pymodoro/logs/ ✅
- Complete configuration interface ✅
- Bug-free timer cycles ✅

### **Phase 6: Refactoring & Infrastructure Improvements** 🔄 (COMPLETE)

**Status**: Technical debt cleanup and architecture improvements

#### **6.1: ConfigProvider Pattern**
- [x] **MAJOR ACHIEVEMENT**: Eliminated all scattered `hasattr(config, '_work_seconds')` checks
- [x] Implemented clean BaseConfig interface with consistent API
- [x] PersistentConfig for normal mode (loads/saves from file)
- [x] InMemoryConfig for test mode (uses provided values, no persistence)
- [x] ConfigProvider singleton with `initialize()` and `get()` methods
- [x] Updated all components to use clean API:
  - [x] Timer Core (`timer/core.py`)
  - [x] Main Window (`gui/main_window.py`)
  - [x] System Tray (`gui/tray.py`)
  - [x] Input Monitor (`input/monitor.py`)
  - [x] Notifications Manager (`notifications/manager.py`)
  - [x] Hotkey Handler (`input/hotkeys.py`)
- [x] Zero conditional checks in business logic
- [x] Better separation between normal and test modes
- [x] Improved maintainability and testability

#### **6.2: Proper Logging Infrastructure** ✅ (COMPLETE)
- [x] Implement structured logging with timestamps and levels
- [x] Log to `~/.config/pymodoro/logs/pymodoro.log` (user-specific location)
- [x] Add command line options: `--log-level DEBUG`, `--log-file /path/file.log`, `--no-clear-log`
- [x] Replace print statements with proper logging
- [x] Simple log management: clear at startup, single file for debugging

#### **6.3: Code Cleanup & Refactoring** ✅ (COMPLETE)
- [x] Remove all hacky `hasattr()` conditional checks
- [x] Consolidate timer logic and eliminate duplication
- [x] Clean up imports and dependencies
- [x] Better separation of concerns
- [x] Improve testability with clean dependency injection
- [x] Code style consistency and documentation

**Deliverables:**
- Clean, maintainable codebase ✅
- Zero conditional config checks in business logic ✅
- Professional logging infrastructure ✅
- Better debugging capabilities ✅
- Improved testability ✅
- Centralized timer control logic ✅
- Eliminated code duplication ✅
- Consistent styling system ✅

### **Phase 7: Sound Alerts** ✅ **COMPLETE**
- [x] Default Linux system sounds integration
- [x] Cross-platform audio playback system
- [x] Sound configuration in settings dialog
- [x] Volume control and sound preview
- [x] Per-event sound customization (work start, break start, session complete)
- [x] Background audio playback without UI blocking
- [x] Fallback audio players (paplay, aplay, ffplay)
- [x] Audio manager with proper cleanup

**Deliverables:**
- Complete audio system with Linux system sounds
- Settings dialog with sound configuration tab
- Volume control and test buttons for each event
- Background audio playback using QThread
- Automatic audio player detection and fallback
- Integration with timer events for automatic sound alerts

**Deliverables:**
- Complete sound alert system
- User-configurable audio feedback
- Integration with Linux audio systems

## Project Structure

```
pymodoro/
├── pymodoro/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── app.py               # Main application class
│   ├── timer/
│   │   ├── __init__.py
│   │   ├── core.py          # Timer logic
│   │   └── states.py        # Timer states
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # Main GUI window
│   │   ├── overlay.py       # Break overlay
│   │   ├── tray.py          # System tray
│   │   └── settings.py      # Settings dialog
│   ├── config/
│   │   ├── __init__.py
│   │   ├── models.py        # Pydantic config models
│   │   └── manager.py       # Config loading/saving
│   ├── input/
│   │   ├── __init__.py
│   │   ├── monitor.py       # Input detection
│   │   └── hotkeys.py       # Global hotkey support
│   ├── notifications/
│   │   ├── __init__.py
│   │   └── manager.py       # Desktop notifications
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py        # Logging utilities
│   └── resources/
│       ├── icons/           # Tray icons
│       └── sounds/          # Alert sounds
├── requirements.txt
├── pyproject.toml
├── README.md
├── ROADMAP.md
└── run.py                   # Simple runner script
```

## Key Dependencies

```txt
PyQt6>=6.6.0
pynput>=1.7.6
pydantic>=2.5.0
plyer>=2.1.0
```

## Current Status: **Production Ready** ✅

All core features implemented and working:
- ✅ Timer with configurable intervals
- ✅ System tray integration with progress display
- ✅ Break overlay with countdown
- ✅ Auto-start after breaks (mouse/keyboard detection)
- ✅ Configuration interface (GUI + tray checkboxes)
- ✅ Global hotkey support (optional)
- ✅ Single persistent notifications (no clutter)
- ✅ Command line test mode support
- ✅ Bug-free operation through complete pomodoro cycles

## Installation & Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install PyQt6 pynput pydantic plyer

# Run application (normal mode)
python run.py

# Run in test mode (5s work, 3s break)
python run.py 5s 3s 2 4s
```

## Next Priority: Phase 6 Refactoring

**Goal**: Clean up technical debt and improve architecture
**Focus**: ConfigProvider pattern, proper logging, code cleanup
**Benefit**: More maintainable, debuggable, and testable codebase

## Total Development Time: **COMPLETED** 

- Phase 1-5: ✅ **DONE** (All core features working)
- Phase 6: 🔄 **COMPLETE** (Refactoring)
- Phase 7+: 📋 **PLANNED** (Future enhancements)

## Success Criteria: **ACHIEVED** ✅

- [x] Timer works reliably with configurable intervals
- [x] System tray integration is seamless
- [x] Break overlay is non-intrusive but effective
- [x] Input detection works without interfering with normal usage
- [x] Configuration persists across sessions
- [x] Application handles edge cases gracefully
- [x] No notification clutter
- [x] No crashes during timer cycles
- [x] Global hotkey support (optional)

## Future Enhancements (v2+)

- Terminal UI using Charm libraries
- Statistics and productivity tracking
- Multiple timer profiles
- Integration with calendar systems
- Customizable break activities
- Plugin system for extensions 