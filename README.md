# 🚀 RAM Optimizer for Mac

A real-time RAM monitoring and optimization tool for macOS with a convenient menu bar interface.

## Features

- **Menu Bar Integration**: Runs as a menu bar app showing real-time memory percentage
- **Expandable Dashboard**: Click the menu bar icon to open a full-featured dashboard
- **Real-time Memory Monitoring**: Continuously monitors memory usage with live updates
- **Visual Dashboard**: Beautiful GUI showing memory statistics and usage graphs
- **Memory Pressure Indicator**: Color-coded indicator showing current memory pressure status
- **Memory Usage History**: Graph showing memory usage over the last 60 seconds
- **Quick Actions**: Fast optimization directly from the menu bar
  - 🧹 **Quick Purge**: Uses macOS `purge` command to free up inactive memory
  - 🗑️ **Clear Caches**: Clears system and user cache files
- **Full Dashboard Controls**:
  - ⚡ **Full Optimization**: Combines cache clearing and memory purging
  - **Auto-Optimization**: Automatically optimizes memory when usage exceeds a threshold
- **Detailed Statistics**: Shows total, used, free, and available memory
- **macOS Notifications**: Get notified when optimization actions complete

## Requirements

- macOS 10.13 or later
- Python 3.10 or later
- Administrator privileges (for purge and cache clearing commands)

> **Note:** This project uses the [`rumps`](https://github.com/jaredks/rumps) library which depends on **PyObjC** — a macOS-only framework. The application will only run on macOS. Additionally, `rumps` works best on Python 3.10+, so 3.9 is not recommended.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/kaivalya-cyber/RAM_Optimizer-for-Mac.git
cd RAM_Optimizer-for-Mac
```

2. Install required dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

Run the application:
```bash
python3 ram_optimizer.py
```

The app will appear in your menu bar as "RAM XX%" showing your current memory usage.

### Menu Bar Features

1. **Memory Display**: Shows current memory usage percentage in real-time (updates every second)
2. **Open Dashboard**: Click to open the full-featured optimization dashboard
3. **Quick Purge**: Fast memory optimization without opening the dashboard
4. **Clear Caches**: Quick cache clearing from the menu
5. **Auto-Optimize**: Toggle automatic optimization when memory exceeds threshold
6. **Quit**: Exit the application

### Dashboard Features

1. **Memory Statistics Panel**: Displays real-time memory information
   - Total Memory
   - Used Memory
   - Free Memory
   - Available Memory
   - Memory Usage Percentage

2. **Memory Pressure Indicator**: 
   - 🟢 Green: Normal (< 50%)
   - 🟡 Yellow: Moderate (50-75%)
   - 🔴 Red: High (> 75%)

3. **Memory Usage Graph**: Shows memory usage trends over the last 60 seconds

4. **Optimization Controls**:
   - **Purge Memory**: Frees up inactive memory using macOS purge command
   - **Clear Caches**: Removes cache files from system and user directories
   - **Full Optimization**: Performs both cache clearing and memory purging

5. **Auto-Optimization**:
   - Enable the checkbox to automatically optimize when memory exceeds threshold
   - Adjust the threshold slider (50-95%)
   - Application will automatically run purge command when threshold is exceeded

## Security Notes

- The `purge` command requires administrator privileges
- Cache clearing modifies system files
- Always review what will be cleared before running optimization
- This tool is provided as-is; use at your own risk

## How It Works

### Menu Bar Integration
- Uses `rumps` library to create a native macOS menu bar application
- Displays real-time memory percentage in the menu bar
- Updates every second with current memory usage
- Runs in the background without appearing in the dock

### Memory Monitoring
- Uses `psutil` library to get real-time memory statistics
- Updates every second with current memory usage
- Maintains 60-second history for graph visualization

### Memory Purging
- Uses macOS built-in `sudo purge` command
- Clears disk cache and inactive memory pages
- May cause brief system freeze (5-10 seconds) during execution

### Cache Clearing
- Removes files from:
  - `~/Library/Caches/*` (User caches)
  - `/Library/Caches/*` (System caches)
  - `/System/Library/Caches/*` (System library caches)
- Frees up disk space and can improve performance

## Troubleshooting

**Application won't start**: Ensure you have Python 3.7+ and all dependencies installed

**Menu bar icon doesn't appear**: Check that the application is running in the background (no dock icon is normal)

**Purge command fails**: Make sure you have administrator privileges and enter your password when prompted

**Cache clearing fails**: Some cache files may be in use; this is normal and safe to ignore

**High memory usage after optimization**: Some applications may rebuild caches; this is normal behavior

**Dashboard won't open**: Make sure the menu bar app is running and click "Open Dashboard" from the menu

## Contributing

### Development Setup

1. Install pre-commit hooks for linting:
```bash
pip3 install pre-commit
pre-commit install
```

2. Linting and formatting is handled by [ruff](https://github.com/astral-sh/ruff). Configuration lives in `pyproject.toml`.

3. Run tests:
```bash
python3 -m pytest test_ram_optimizer.py -v
```

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool modifies system files and memory. Use at your own risk. The developers are not responsible for any data loss or system issues that may occur.

## Author

Created by Kaivalya Singh

## Acknowledgments

- Built with Python, tkinter, psutil, matplotlib, and rumps
- Inspired by macOS memory management tools
- Menu bar functionality powered by rumps library
