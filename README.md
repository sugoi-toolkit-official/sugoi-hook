# Sugoi Hook - Modern Text Extraction GUI

A beautiful and user-friendly GUI with **dual-engine support** for both **Textractor** and **Luna Hook**, designed for extracting text from games and applications in real-time.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)

## Contact

For any queries, support, or discussions, join the **Sugoi Toolkit Discord Server**:

🔗 [Join Sugoi Toolkit Server](https://discord.gg/XFbWSjMHJh)

---

## Features

### Dual-Engine Support
Sugoi Hook now supports **two powerful hooking engines** that you can switch between seamlessly:

- **Luna Hook (Default)**: Advanced hooking engine with robust compatibility
  - Excellent support for modern games and applications
  - Enhanced text extraction capabilities
  - Built on LunaTranslator's proven hooking technology
  
- **Textractor**: Classic and reliable hooking engine
  - Wide compatibility with legacy applications
  - Extensive hook code library
  - Battle-tested text extraction

**Switch engines on-the-fly** using the toggle in the header - the GUI will automatically handle process detachment and re-attachment when switching engines.

### Core Functionality
- **Dual-Engine Support**: Choose between Luna Hook and Textractor engines
- **Process Attachment**: Attach to any running process with intelligent filtering
- **Hook Management**: Automatic hook discovery and manual hook code support
- **Real-time Text Extraction**: Live text capture with statistics tracking
- **Plugin System**: Extensible architecture for text processing and filtering
- **Modern UI**: Beautiful dark-themed interface with DPI scaling support

### Advanced Features
- **Game Profiles**: Save hook configurations per game and auto-launch with saved settings
- **Smart Process Filtering**: Automatically filters out system processes and bloatware
- **Process Icons**: High-quality icon extraction for easy identification
- **Manual Hook Codes**: Support for H-codes and R-codes with built-in syntax help
- **Auto-copy**: Automatically copy extracted text to clipboard (enabled by default, copies non-console text only)
- **System Tray**: Minimize to tray for background operation
- **Statistics**: Track lines, words, characters, and extraction rate
- **Export**: Save extracted text to file

### Plugin System
Built-in plugins for text processing:
- **Remove Empty Lines**: Filter out empty text
- **Remove Special Characters**: Clean unwanted characters
- **Remove Duplicates**: Eliminate duplicate text entries
- **Minimum Length Filter**: Filter text by minimum length
- **Fix Repeated Characters**: Fix repeated character patterns in text
- **Google Translate**: Real-time extracted text translation
- **Translation Proxy**: Forward extracted text to Translator++ via HTTP proxy contributed by [Dream Savior on Patreon](https://www.patreon.com/cw/dreamsavior)
- **Overlay Window**: Display extracted text as an overlay on screen (optional)

**Plugin Features:**
- **Drag & Drop Reordering**: Reorder plugins by dragging them in the list
- **Persistent Order**: Plugin order and active states are saved and restored on restart
- **Sequential Processing**: Text is processed through plugins in the order they appear

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

### Game Profiles

Sugoi Hook automatically saves hook configurations for your games, making it easy to launch and play with a single click.

1. **Automatic Profile Saving**
   - When you attach to a game and select a hook, the configuration is automatically saved
   - Profiles include hook type (auto/manual), hook data, function name, and engine used
   - Each game is uniquely identified by its executable path and file size

2. **Launch from Profile Manager**
   - Click "💾 Game Profiles" to open the profile manager
   - View all your saved game profiles with hook information and last used date
   - Double-click a game or click "🚀 Launch Game" to auto-launch
   - The game will start, attach automatically, and apply the saved hook

3. **Browse and Launch Games**
   - Click "📂 Browse for EXE" to manually select any executable file
   - The GUI will launch it and auto-attach when the process starts
   - Perfect for adding new games to your profile collection

### Plugin Management

1. **Activate/Deactivate Plugins**
   - Double-click a plugin in the Plugins section to toggle it
   - Right-click a plugin for quick access to activate/deactivate options
   - Active plugins process text in the order they appear

2. **Configure Plugin Settings**
   - Right-click a plugin and select "⚙️ Configure" to access its settings
   - Plugins can have configurable options like language selection, filtering rules, or display preferences
   - Settings are automatically saved and restored when you restart the application
   - Not all plugins have configurable settings - this option only appears for plugins that support it

3. **Reorder Plugins**
   - Drag and drop plugins in the list to change their execution order
   - The first plugin in the list is applied first, then the next, and so on
   - Plugin order is automatically saved and restored on restart

4. **Add Custom Plugins**
   - Click "📂 Open Folder" to access the plugins directory
   - Create a new `.py` file following the plugin template
   - Click "🔄 Refresh" to load new plugins

5. **Plugin Development**
   ```python
   from plugins import TextractorPlugin

   class MyPlugin(TextractorPlugin):
       name = "My Custom Plugin"
       description = "Does something cool"
       version = "1.0"
       
       def process_text(self, text: str) -> str | None:
           # Process and return text, or None to filter it out
           return text.upper()
       
       def get_settings(self) -> dict:
           # Optional: provide configurable settings
           return {
               'my_setting': (True, 'bool', 'Enable my feature')
           }
       
       def set_setting(self, name: str, value) -> bool:
           # Optional: handle setting changes
           if name == 'my_setting':
               self.my_setting = value
               return True
           return False
   
   plugin = MyPlugin()
   ```

### Keyboard Shortcuts

- `F11` - Toggle fullscreen mode
- `Escape` - Exit fullscreen mode
- `Double-click` - Quick actions (attach to process, select hook, toggle plugin)

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
├── SugoiHook_gui.py              # Main application with dual-engine support
├── plugins/                       # Plugin system
│   ├── __init__.py               # Plugin base class
│   ├── remove_empty.py           # Built-in plugins
│   ├── remove_duplicates.py
│   ├── remove_special_chars.py
│   ├── min_length_filter.py
│   ├── fix_repeated_chars.py
│   ├── google_translate.py
│   ├── translation_proxy.py      # External translation tool proxy
│   └── overlay_window.py
├── Translator/                    # Translation module
│   └── deep_translator/          # Translation library
├── textractor_builds/             # Textractor engine binaries
│   ├── _x86/                     # 32-bit Textractor CLI
│   └── _x64/                     # 64-bit Textractor CLI
├── luna_builds/                   # Luna Hook engine binaries
│   ├── LunaHostCLI32.exe         # 32-bit Luna Host CLI
│   ├── LunaHostCLI64.exe         # 64-bit Luna Host CLI
│   ├── LunaHook32.dll            # 32-bit Luna Hook library
│   ├── LunaHook64.dll            # 64-bit Luna Hook library
│   ├── LunaHost32.dll
│   └── LunaHost64.dll
├── logo.webp                      # Application icon
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Compilation

To build an executable, simply run:
```bash
build.bat
```

This will compile the application into a standalone executable using Nuitka.

## Acknowledgments

Sugoi Hook is built on the foundation of powerful open-source text hooking technologies and community contributions. We are deeply grateful to the following projects and contributors:

### Hooking Engines

#### Textractor
This project integrates [Textractor](https://github.com/Chenx221/Textractor), a modified version of the original Textractor by Artikash. **Textractor** is a powerful and battle-tested text hooking tool that enables real-time text extraction from games and applications.

- **Original Textractor**: [Artikash/Textractor](https://github.com/Artikash/Textractor)
- **Modified Textractor**: [Chenx221/Textractor](https://github.com/Chenx221/Textractor)

#### Luna Hook
Sugoi Hook integrates **Luna Hook** (LunaHook.dll) for advanced text extraction capabilities. Luna Hook is sourced from the [LunaTranslator](https://github.com/HIllya51/LunaTranslator) project, an excellent translation tool with robust hooking technology.

- **Luna Hook DLLs**: Sourced from [LunaTranslator](https://github.com/HIllya51/LunaTranslator/tree/main/src/) by HIllya51
- **LunaHostCLI**: Custom CLI interface developed by **Team Sugoi Toolkit** to integrate Luna Hook with our GUI

### Development

- **Sugoi Hook GUI**: Modern interface, dual-engine system, and plugin architecture developed by **Team Sugoi Toolkit**
- **Plugin System**: Extensible architecture for community-driven text processing
- **Dual-Engine Integration**: Seamless switching between Textractor and Luna Hook engines

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.


**Note**: This tool is designed for legitimate purposes such as translation assistance and accessibility. Please respect software licenses and terms of service when using text extraction tools.

---

<div align="center">
  <b>Made with ❤️ by Team Sugoi Toolkit</b>
</div>
