# 🚀 RAM Optimizer for Mac

A real-time RAM monitoring and optimization tool for macOS built with Python.

## Features

- **Real-time Memory Monitoring**: Continuously monitors memory usage with live updates
- **Visual Dashboard**: Beautiful GUI showing memory statistics and usage graphs
- **Memory Pressure Indicator**: Color-coded indicator showing current memory pressure status
- **Memory Usage History**: Graph showing memory usage over the last 60 seconds
- **Manual Optimization**:
  - 🧹 **Purge Memory**: Uses macOS `purge` command to free up inactive memory
  - 🗑️ **Clear Caches**: Clears system and user cache files
  - ⚡ **Full Optimization**: Combines cache clearing and memory purging
- **Auto-Optimization**: Automatically optimizes memory when usage exceeds a threshold
- **Detailed Statistics**: Shows total, used, free, and available memory

## Requirements

- macOS 10.13 or later
- Python 3.7 or later
- Administrator privileges (for purge and cache clearing commands)

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

### Features Overview

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

3. **Memory Usage Graph**: Shows memory usage trends over time

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

**Purge command fails**: Make sure you have administrator privileges and enter your password when prompted

**Cache clearing fails**: Some cache files may be in use; this is normal and safe to ignore

**High memory usage after optimization**: Some applications may rebuild caches; this is normal behavior

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool modifies system files and memory. Use at your own risk. The developers are not responsible for any data loss or system issues that may occur.

## Author

Created by Kaivalya Singh

## Acknowledgments

- Built with Python, tkinter, psutil, and matplotlib
- Inspired by macOS memory management tools
