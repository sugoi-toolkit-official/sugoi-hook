# Sugoi Hook - Modern Text Extraction GUI

A beautiful and user-friendly GUI wrapper for Textractor CLI, designed for extracting text from games and applications in real-time.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)

## Features

### Core Functionality
- **Process Attachment**: Attach to any running process with intelligent filtering
- **Hook Management**: Automatic hook discovery and manual hook code support
- **Real-time Text Extraction**: Live text capture with statistics tracking
- **Plugin System**: Extensible architecture for text processing and filtering
- **Modern UI**: Beautiful dark-themed interface with DPI scaling support

### Advanced Features
- **Smart Process Filtering**: Automatically filters out system processes and bloatware
- **Process Icons**: High-quality icon extraction for easy identification
- **Manual Hook Codes**: Support for H-codes and R-codes with built-in syntax help
- **Auto-copy**: Automatically copy extracted text to clipboard
- **System Tray**: Minimize to tray for background operation
- **Statistics**: Track lines, words, characters, and extraction rate
- **Export**: Save extracted text to file

### Plugin System
Built-in plugins for text processing:
- **Remove Empty Lines**: Filter out empty text
- **Remove Special Characters**: Clean unwanted characters
- **Remove Duplicates**: Eliminate duplicate text entries
- **Minimum Length Filter**: Filter text by minimum length
- **Google Translate**: Real-time extracted text translation
- **Overlay Window**: Display extracted text as an overlay on screen (optional)

## Quick Start

### Prerequisites
- Windows 10/11
- Python 3.11 or higher (for running from source)

### Installation

#### Option 1: Use Pre-built Executable (Recommended)
Download the latest release from the [Releases](https://github.com/sugoi-toolkit-official/sugoi-hook/releases) page and run `SugoiHook.exe`.

#### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/sugoi-toolkit-official/sugoi-hook.git
cd sugoi-hook

# Install dependencies
pip install -r requirements.txt

# Run the application
python SugoiHook_gui.py
```

## How to Use

### Basic Workflow

1. **Select a Process**
   - Browse the process list or use the search bar
   - Double-click a process to attach
   - The GUI filters out system processes automatically

2. **Choose a Hook**
   - Wait for hooks to appear as you interact with the application
   - Double-click a hook to select it
   - Or use manual hook codes for advanced usage

3. **Extract Text**
   - Text will appear in real-time in the output area
   - Use plugins to filter and process the text
   - Save or copy the extracted text as needed

### Manual Hook Codes

Sugoi Hook supports Textractor hook codes for advanced users:

**H-Codes (Hook Codes)**
```
HB4@0                    # Hook at address 0, ANSI single char, offset 4
HS-4@12345               # Hook at 0x12345, ANSI string, offset -4
HQ@401000:user32.dll     # Hook in user32.dll, Unicode string
```

**R-Codes (Read Codes)**
```
RS@401000               # Read ANSI string at address
RQ@401000               # Read Unicode string at address
```

Click the ❓ button in the GUI for complete syntax documentation.

### Plugin Management

1. **Activate/Deactivate Plugins**
   - Double-click a plugin in the Plugins section to toggle it
   - Active plugins process text in order

2. **Add Custom Plugins**
   - Click "📂 Open Folder" to access the plugins directory
   - Create a new `.py` file following the plugin template
   - Click "🔄 Refresh" to load new plugins

3. **Plugin Development**
   ```python
   from plugins import TextractorPlugin

   class MyPlugin(TextractorPlugin):
       name = "My Custom Plugin"
       description = "Does something cool"
       version = "1.0"
       
       def process_text(self, text: str) -> str | None:
           # Process and return text, or None to filter it out
           return text.upper()
   
   plugin = MyPlugin()
   ```

## Architecture

### Core Logic

Sugoi Hook uses a multi-threaded architecture:

1. **Main Thread**: Handles UI rendering and user interactions
2. **CLI Process Thread**: Manages communication with TextractorCLI.exe
3. **Output Reader Thread**: Reads and parses text from the CLI process
4. **Plugin Processing**: Sequential text processing through active plugins

### Text Flow
```
Application → TextractorCLI → Hook Detection → Text Extraction
    ↓
Plugin Chain (Filter/Transform) → UI Display → Auto-copy (optional)
```

### Process Filtering

The application uses multiple heuristics to filter processes:
- **System directories**: Excludes processes from Windows system folders
- **Process patterns**: Filters known system processes and bloatware
- **Window detection**: Only shows processes with visible windows
- **PID filtering**: Excludes very low PIDs (system processes)

## Technical Details

### Dependencies
- **tkinter**: GUI framework
- **psutil**: Process management
- **Pillow (PIL)**: Image processing for icons
- **pywin32**: Windows API access
- **pystray**: System tray support (optional)

### File Structure
```
sugoi-hook/
├── SugoiHook_gui.py          # Main application
├── plugins/                   # Plugin system
│   ├── __init__.py           # Plugin base class
│   ├── remove_empty.py       # Built-in plugins
│   ├── remove_duplicates.py
│   ├── remove_special_chars.py
│   └── min_length_filter.py
├── Translator/                # Translation module
│   └── deep_translator/      # Translation library
├── builds/                    # TextractorCLI binaries
│   ├── _x86/                 # 32-bit CLI
│   └── _x64/                 # 64-bit CLI
├── logo.webp                  # Application icon
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Compilation

To build an executable, simply run:
```bash
build.bat
```

This will compile the application into a standalone executable using Nuitka.

## Acknowledgments

This project is built on top of [Textractor](https://github.com/Chenx221/Textractor), a modified version of the original Textractor by Artikash. We are grateful for their contribution to the text extraction community.

**Textractor** is a powerful text hooking tool that enables real-time text extraction from games and applications. Sugoi Hook provides a modern, user-friendly interface to make Textractor more accessible.

### Credits
- **Original Textractor**: [Artikash/Textractor](https://github.com/Artikash/Textractor)
- **Modified Textractor**: [Chenx221/Textractor](https://github.com/Chenx221/Textractor)
- **Sugoi Hook GUI**: Modern interface and plugin system

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

## Contact

For any queries, support, or discussions, join the **Sugoi Toolkit Discord Server**:

🔗 [Join Sugoi Toolkit Server](https://discord.gg/XFbWSjMHJh)

---

**Note**: This tool is designed for legitimate purposes such as translation assistance and accessibility. Please respect software licenses and terms of service when using text extraction tools.

---

<div align="center">
  <b>Made with ❤️ by Team Sugoi Toolkit</b>
</div>
