# Changelog

All notable changes to RAM Optimizer will be documented in this file.

## [1.0.0] - 2026-06-25

### Added
- macOS menu bar integration with real-time RAM/CPU display
- Expandable tkinter dashboard with memory statistics, swap, CPU, uptime, boot time, CPU temperature, and network I/O
- Memory pressure indicator with color-coded bar (Normal/Moderate/High)
- Memory usage history graph (last 60 seconds) via matplotlib
- Top memory-consuming processes in a sortable Treeview with right-click kill capability
- Quick actions from menu bar: Quick Purge, Clear Caches, View Logs
- Dashboard controls: Purge Memory, Clear Caches, Full Optimization, Export CSV
- Auto-optimization with configurable threshold slider and battery-aware toggle
- Customizable memory alerts with cooldown (macOS notifications)
- Scheduled optimization at configurable intervals
- macOS login launch option (LaunchAgent plist)
- Dark/light theme toggle with widget registry system
- Optimization action logging with log viewer window
- Persistent JSON settings for all configuration
- 21 unit tests covering settings, formatting, logs, memory history, cache paths, and toggles
- CI workflow (GitHub Actions) on macos-latest, Python 3.10-3.12
- Pre-commit hooks with ruff (lint + format)
- Makefile with install, test, lint, format, check, clean, help targets
- EditorConfig for consistent editor settings
- Security policy (SECURITY.md)

### Fixed
- Missing `save_settings()` and `update_threshold()` methods in Dashboard class causing crashes
- Duplicate `create_stat_label` method definition
- Menu bar auto-optimize toggle crashing when dashboard hadn't been opened
- `dark_mode` theme preference not persisted across sessions
- Menu bar not syncing auto-optimize threshold from dashboard changes
- Cache clearing commands using tilde expansion with sudo (now uses absolute paths)

### Changed
- Python requirement bumped from 3.7 to 3.10+
- `IOError` replaced with `OSError` throughout
- `super()` call modernized (Python 3 style)
- Imports sorted and linted with ruff
- CI uses `make check` (lint + test) instead of raw pytest
- DRY: extracted `_get_user_cache_path()` static helper for cache path resolution

---

## Pre-release history

### [0.5.0] - Various commits
- feat: add dark/light theme toggle, scheduled optimization, and macOS startup launch option
- feat: add process kill capability with right-click context menu on Treeview

### [0.4.0] - Various commits
- feat: add network usage monitor with real-time I/O stats
- feat: add CPU temperature monitoring via macOS sensors
- feat: add system uptime and boot time display to dashboard

### [0.3.0] - Various commits
- feat: add export memory history to CSV functionality
- feat: add optimization action logging with log viewer
- feat: add battery-aware optimization to disable auto-optimize on battery power

### [0.2.0] - Various commits
- feat: add customizable memory alerts with cooldown and notifications
- feat: add persistent JSON settings for auto-optimize config
- feat: add top processes monitor with Treeview to dashboard
- feat: add CPU usage monitor to dashboard and menu bar
- feat: add swap memory monitoring to dashboard

### [0.1.0] - Initial release
- Initial commit: Real-time RAM Optimizer for Mac with GUI dashboard, memory monitoring, and optimization features
- macOS menu bar integration with rumps
- Memory purge and cache clearing functionality
