# Uma Friend Point Farm Automation

A Python-based automation script for the Uma Musume mobile game that automates the friend point farming process using ADB (Android Debug Bridge) and template matching.

## 🎯 Overview

This automation script is specifically designed for **emulators** and performs a complex 18-step loop to farm friend points in Uma Musume. It uses computer vision to identify UI elements on screen and automates the entire process, including:

- Career mode navigation
- Auto-selection of options
- TP charging when needed
- Skip functionality
- Menu navigation
- Give up and restart cycle

**⚠️ Important Requirements:**
- **Resolution**: Must be **1080x1920** (portrait mode)
- **Starting Position**: Must begin on the **Home screen** where the Career button appears
- **Emulator**: Tested on Mumu Emulator, but compatible with any emulator meeting the resolution requirement

## ✨ Features

- **ADB Integration**: Connects to Android devices via ADB for screen capture and control
- **Template Matching**: Uses OpenCV to find and interact with UI elements
- **Smart Recovery**: Implements intelligent retry mechanisms and fallback logic
- **TP Charge Automation**: Automatically handles TP restoration when needed
- **Configurable Settings**: External configuration file for easy customization
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Error Handling**: Robust error handling with automatic recovery

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- **Emulator** (tested on Mumu Emulator, but any emulator works)
- **1080x1920 resolution** (portrait mode) - **REQUIRED**
- ADB (Android Debug Bridge) installed and in PATH
- USB debugging enabled on your emulator

### Installation

1. **Clone or download the project files**
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your emulator**:
   - Enable USB debugging on your emulator
   - **Set resolution to 1080x1920 (portrait mode)**
   - **Ensure you're on the Home screen where the Career button appears**
   - Connect emulator via ADB
   - Update `config.json` with your emulator's ADB address

4. **Run the automation**:
   ```bash
   python uma_automation.py
   ```

## ⚙️ Configuration

Edit `config.json` to customize the automation:

```json
{
  "adb": {
    "device_address": "127.0.0.1:16416",
    "screenshot_path": "./screenshots",
    "template_path": "./assets/buttons"
  },
  "automation": {
    "wait_time": {
      "career": 10,
      "next": 1,
      "start_career": 2,
      "skip": 1,
      "confirm": 5,
      "loop": 5
    },
    "attempts": {
      "next": 10,
      "next_check": 5
    },
    "coordinates": {
      "tap_after_skip": [249, 948]
    }
  }
}
```

### Configuration Options

- **`device_address`**: Your emulator's ADB connection address (default: 127.0.0.1:16416 or 7555 for Mumu)
- **`wait_time`**: Customizable delays for different operations
- **`attempts`**: Number of retry attempts for finding elements
- **`coordinates`**: Fixed screen coordinates for 1080x1920 resolution

## 🔧 Setup Instructions

### 1. Install ADB

**Windows:**
- Download [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
- Extract and add to system PATH

**macOS/Linux:**
```bash
# macOS
brew install android-platform-tools

# Ubuntu/Debian
sudo apt-get install android-tools-adb
```

### 2. Set Up Emulator

**For Mumu Emulator (Recommended):**
1. Download and install [Mumu Emulator](https://mumu.163.com/)
2. **Set resolution to 1080x1920 (portrait mode)**
3. Enable USB debugging in emulator settings
4. **Ensure you're on the Home screen where the Career button appears**

**For Other Emulators:**
1. Install your preferred Android emulator
2. **Set resolution to 1080x1920 (portrait mode)**
3. Enable USB debugging in emulator settings
4. **Ensure you're on the Home screen where the Career button appears**

### 3. Connect Emulator

**For Mumu Emulator:**
```bash
adb connect 127.0.0.1:16416
```

**For Other Emulators:**
```bash
# Check available devices
adb devices

# Connect via network (if supported)
adb connect YOUR_EMULATOR_IP:5555
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Test Setup

```bash
python test_setup.py
```

## 🚀 Usage

### Basic Usage

```bash
python uma_automation.py
```

### Windows Batch File

Double-click `run_automation.bat` for easy execution on Windows.

### Custom Configuration

1. Edit `config.json` with your settings
2. Ensure all template images are in `assets/buttons/`
3. Run the automation script

## 📊 Monitoring

The script provides comprehensive logging:

- **INFO**: Normal operation steps
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures requiring attention

Logs include:
- Step-by-step progress
- Element detection results
- Timing information
- Error details and recovery actions

### Debug Mode

Enable debug logging by modifying the script:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## 🔒 Safety Features

- **Automatic Recovery**: Script attempts to recover from most errors
- **Cycle Restart**: Automatically restarts failed automation cycles
- **Timeout Protection**: Prevents infinite hangs on unresponsive elements
- **Graceful Exit**: Ctrl+C stops automation safely

## 📝 Customization

### Modifying Wait Times

Edit the `wait_time` section in `config.json`:

```json
"wait_time": {
  "career": 15,        # Increase career wait time
  "next": 2,           # Increase next button wait time
  "start_career": 3    # Increase start career wait time
}
```

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and automation purposes. Use at your own risk and in accordance with the game's terms of service.

## ⚠️ Disclaimer

- This automation script is for educational purposes
- Use responsibly and in accordance with game terms of service
- The authors are not responsible for any consequences of use
- Always test on a test account first

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Verify your setup matches the requirements
4. Check that all template images are present and correct

**Happy Farming! 🐎✨**
