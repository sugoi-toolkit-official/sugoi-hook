#!/usr/bin/env python3
"""
SugoiHook GUI - Modern Text Extraction Interface
Built on top of Textractor by Artikash (https://github.com/Chenx221/Textractor)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import psutil
import os
import re
import sys
import time
import importlib.util
import json
import hashlib
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import win32gui
import win32ui
import win32con
import win32api
import win32process
import ctypes
try:
    import pystray
    from pystray import MenuItem as item
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False

# Import plugin base class
try:
    from plugins import TextractorPlugin
    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False

class ModernTextractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Sugoi Hook - Modern Text Extraction")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Color schemes for light/dark mode
        self.dark_colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'primary': '#89b4fa',
            'secondary': '#f38ba8',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'surface': '#313244',
            'surface_light': '#45475a',
            'border': '#585b70',
            'text': '#cdd6f4',
            'text_dim': '#9399b2',
            'accent': '#b4befe'
        }
        
        self.light_colors = {
            'bg': '#eff1f5',
            'fg': '#4c4f69',
            'primary': '#1e66f5',
            'secondary': '#d20f39',
            'success': '#40a02b',
            'warning': '#df8e1d',
            'surface': '#e6e9ef',
            'surface_light': '#ccd0da',
            'border': '#9ca0b0',
            'text': '#4c4f69',
            'text_dim': '#6c6f85',
            'accent': '#7287fd'
        }
        
        # Current theme - dark mode is default
        self.colors = self.dark_colors.copy()
        
        # Calculate DPI scale factor
        try:
            # Get the DPI from the window system
            # 96 is the standard DPI (100% scaling)
            dpi = self.root.winfo_fpixels('1i')
            self.scale_factor = dpi / 96.0
        except Exception:
            self.scale_factor = 1.0
        
        # Apply scaling to window size
        width = int(1000 * self.scale_factor)
        height = int(750 * self.scale_factor)
        self.root.geometry(f"{width}x{height}")
        
        min_width = int(900 * self.scale_factor)
        min_height = int(650 * self.scale_factor)
        self.root.minsize(min_width, min_height)
        
        # State variables
        self.cli_process = None
        self.attached_pid = None
        self.hooks = {}
        self.selected_hook_id = None
        self.is_reading = False
        self.process_icons = {}
        self.is_fullscreen = False
        
        # Plugin system (paths set after base_path is determined)
        self.plugins = {}  # Dictionary of loaded plugins: {filename: plugin_instance}
        self.active_plugins = []  # List of active plugin filenames
        self.plugin_order = []  # List of all plugin filenames in display/execution order
        self.plugins_config_path = None  # Set after base_path
        self.plugins_folder = None  # Set after base_path
        self.plugin_settings = {}  # Dictionary of plugin settings: {filename: {setting_name: value}}
        
        # Game profiles system for auto-hook saving/loading
        self.game_profiles = {}  # Dictionary of saved game hook profiles
        self.game_profiles_path = None  # Set after base_path
        self.current_game_id = None  # ID of currently attached game
        self.auto_hook_pending = False  # Flag for pending auto-hook
        self.auto_hook_data = None  # Saved hook data for auto-selection
        
        # Auto-copy settings - enabled by default
        self.auto_copy_enabled = tk.BooleanVar(value=True)
        
        # Statistics tracking
        self.stats = {
            'lines': 0,
            'words': 0,
            'chars': 0,
            'start_time': None,
            'last_update': time.time()
        }
        
        # System tray
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
        # System directories to check for filtering
        self.system_dirs = [
            'c:\\windows\\system32',
            'c:\\windows\\syswow64',
            'c:\\windows\\systemapps',
            'c:\\windows\\winsxs',
            'c:\\program files\\windows',
            'c:\\program files (x86)\\windows',
            'c:\\program files\\windowsapps',
            'c:\\program files (x86)\\windowsapps',
        ]
        
        # Known system process patterns (case-insensitive)
        self.system_process_patterns = [
            'svchost', 'dllhost', 'conhost', 'runtimebroker', 'taskhostw',
            'sihost', 'csrss', 'smss', 'wininit', 'services', 'lsass',
            'winlogon', 'fontdrvhost', 'dwm', 'audiodg', 'spoolsv',
            'searchindexer', 'searchhost', 'searchprotocolhost', 'searchfilterhost',
            'startmenuexperiencehost', 'shellexperiencehost', 'textinputhost',
            'securityhealthservice', 'securityhealthsystray', 'smartscreen',
            'applicationframehost', 'systemsettings', 'lockapp', 'winstore.app',
            'microsoftedge', 'msedge', 'identity helper', 'crashpad_handler',
        ]
        
        # Known bloatware/utility patterns
        self.bloatware_patterns = [
            'nvidia', 'amd', 'intel', 'realtek', 'asus', 'msi', 'gigabyte',
            'corsair', 'razer', 'logitech', 'steelseries', 'creative',
            'onedrive', 'dropbox', 'googledrive', 'icloud', 'backup',
            'antivirus', 'defender', 'malwarebytes', 'avast', 'avg', 'norton',
            'mcafee', 'kaspersky', 'bitdefender', 'eset', 'sophos',
            'chrome', 'firefox', 'edge', 'opera', 'brave', 'vivaldi', 'safari',
            'discord', 'slack', 'teams', 'zoom', 'skype', 'telegram', 'whatsapp',
            'spotify', 'itunes', 'vlc', 'winamp', 'foobar', 'musicbee',
            'steam', 'epic', 'origin', 'uplay', 'battlenet', 'gog', 'riot',
            'vanguard', 'easyanticheat', 'battleye', 'gameguard',
            'obs', 'streamlabs', 'xsplit', 'nvidia share', 'amd link',
            'notepad++', 'sublime', 'atom', 'brackets', 'code', 'vscode',
            'pycharm', 'intellij', 'eclipse', 'netbeans', 'visual studio',
            'winrar', '7zip', 'winzip', 'peazip', 'bandizip',
            'ccleaner', 'defraggler', 'recuva', 'speccy', 'hwmonitor',
            'cpuz', 'gpuz', 'hwinfo', 'crystaldisk', 'msiafterburner',
            'python', 'java', 'node', 'ruby', 'php', 'perl', 'go',
            'powershell', 'cmd', 'terminal', 'git', 'svn', 'tortoise',
        ]
        
        # Specific executables to always exclude
        self.excluded_executables = {
            'system', 'registry', 'idle', 'system idle process',
            'explorer.exe', 'taskmgr.exe', 'ctfmon.exe',
            'winword.exe', 'excel.exe', 'powerpnt.exe', 'outlook.exe',
            'acrobat.exe', 'acrord32.exe', 'foxit reader.exe',
            'notepad.exe', 'mspaint.exe', 'calc.exe', 'snippingtool.exe',
            'textractor.exe', 'textractorcli.exe', 'textractorgui.exe',
            'textractor_gui.exe' , 'sugoi_hook.exe'
        }
        
        # Determine CLI paths - handle both development and compiled modes
        # Check for both PyInstaller (frozen) and Nuitka (__compiled__)
        # Also check for standalone executable (Nuitka onefile might not set __compiled__ on sys)
        is_frozen = getattr(sys, 'frozen', False)
        is_nuitka = getattr(sys, '__compiled__', False) or (
            sys.executable.lower().endswith('.exe') and 
            'python' not in os.path.basename(sys.executable).lower()
        )
        
        is_compiled = is_frozen or is_nuitka
        
        if is_compiled:
            # Running as compiled executable
            if is_frozen:
                # PyInstaller mode
                self.base_path = Path(sys._MEIPASS)
                self.app_path = Path(sys.executable).parent
            else:
                # Nuitka mode - onefile unpacks assets to temp directory
                self.base_path = Path(__file__).parent
                self.app_path = Path(sys.executable).parent
            
            # Use user_data_dir as the directory where the executable is located
            self.user_data_dir = self.app_path
            self.plugins_folder = self.user_data_dir / "plugins"
            self.plugins_config_path = self.user_data_dir / "plugins_config.json"
            
            # Ensure user data directory exists
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Do not copy bundled plugins or translator to Documents
            # Instead, rely on them being present next to the executable
            # self.copy_bundled_plugins()
            # self.copy_bundled_translator()
            
        else:
            # Running as Python script
            self.base_path = Path(__file__).parent
            self.app_path = self.base_path
            self.plugins_folder = self.app_path / "plugins"
        self.plugins_config_path = self.app_path / "plugins_config.json"
        self.game_profiles_path = self.app_path / "game_profiles.json"
        
        # Textractor paths
        self.textractor_x86_path = self.base_path / "textractor_builds" / "_x86" / "TextractorCLI.exe"
        self.textractor_x64_path = self.base_path / "textractor_builds" / "_x64" / "TextractorCLI.exe"
        
        # Luna Hook paths
        self.luna_x86_path = self.base_path / "luna_builds" / "LunaHostCLI32.exe"
        self.luna_x64_path = self.base_path / "luna_builds" / "LunaHostCLI64.exe"
        
        self.logo_path = self.base_path / "logo.webp"
        
        # Engine selection - Luna as default
        self.current_engine = "luna"
        
        # Initialize plugin system
        self.init_plugin_system()
        
        # Check if CLI executables exist for both engines
        textractor_exists = self.textractor_x86_path.exists() or self.textractor_x64_path.exists()
        luna_exists = self.luna_x86_path.exists() or self.luna_x64_path.exists()
        
        if not textractor_exists and not luna_exists:
            messagebox.showerror("Error", 
                "No hook engine executables found!\n\n"
                "Expected locations:\n"
                f"Textractor: {self.textractor_x86_path} or {self.textractor_x64_path}\n"
                f"Luna: {self.luna_x86_path} or {self.luna_x64_path}")
            sys.exit(1)
        
        # Set default engine based on availability
        if not luna_exists and textractor_exists:
            self.current_engine = "textractor"
        elif not textractor_exists and luna_exists:
            self.current_engine = "luna"
        
        self.setup_modern_theme()
        self.set_window_icon()
        self.create_status_bar()
        self.setup_ui()
        self.setup_system_tray()
        self.refresh_processes()
        self.update_status_bar()
        
        # Bind fullscreen detection
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.root.bind('<Configure>', self.on_window_configure)
        
    def scale(self, value):
        """Scale a value based on DPI"""
        return int(value * self.scale_factor)

    def copy_bundled_plugins(self):
        """Copy bundled plugins to the user's documents folder"""
        try:
            # Find bundled plugins folder
            bundled_plugins_path = self.base_path / "plugins"
            
            if not bundled_plugins_path.exists():
                bundled_plugins_path = self.app_path / "plugins"
            
            if not bundled_plugins_path.exists():
                return

            # Create destination folder
            self.plugins_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy each plugin file
            import shutil
            for plugin_file in bundled_plugins_path.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                    
                dest_file = self.plugins_folder / plugin_file.name
                
                # Only copy if it doesn't exist to avoid overwriting user changes
                if not dest_file.exists():
                    try:
                        shutil.copy2(plugin_file, dest_file)
                    except Exception:
                        pass
                        
        except Exception:
            pass

    def copy_bundled_translator(self):
        """Copy bundled Translator folder to the user's documents folder"""
        try:
            import shutil
            
            # Find bundled Translator folder - look next to the executable first
            bundled_translator_path = self.app_path / "Translator"
            
            # If not found next to exe, try base_path (for bundled resources)
            if not bundled_translator_path.exists():
                bundled_translator_path = self.base_path / "Translator"
            
            if not bundled_translator_path.exists():
                return

            # Destination folder
            dest_translator_path = self.user_data_dir / "Translator"
            
            # Create destination folder if it doesn't exist
            dest_translator_path.mkdir(parents=True, exist_ok=True)
            
            # Recursively copy all files and directories
            self._copy_directory_contents(bundled_translator_path, dest_translator_path)
                        
        except Exception:
            pass
    
    def _copy_directory_contents(self, src_dir, dest_dir):
        """Recursively copy directory contents, only copying files that don't exist"""
        import shutil
        
        try:
            # Ensure destination directory exists
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Iterate through all items in source directory
            for item in src_dir.iterdir():
                dest_item = dest_dir / item.name
                
                if item.is_dir():
                    # Recursively copy subdirectory
                    self._copy_directory_contents(item, dest_item)
                elif item.is_file():
                    # Only copy if file doesn't exist to avoid overwriting user changes
                    if not dest_item.exists():
                        try:
                            shutil.copy2(item, dest_item)
                        except Exception:
                            pass
        except Exception:
            pass

    # ==================== PLUGIN SYSTEM METHODS ====================
    
    def init_plugin_system(self):
        """Initialize the plugin system"""
        # Ensure plugins folder exists regardless of PLUGINS_AVAILABLE logic
        if not self.plugins_folder.exists():
            self.plugins_folder.mkdir(parents=True, exist_ok=True)
            
        if not PLUGINS_AVAILABLE:
            return
        
        # Load saved plugin configuration
        self.load_plugins_config()
        
        # Discover and load available plugins
        self.discover_plugins()
    
    def discover_plugins(self):
        """Discover all available plugins in the plugins folder"""
        if not self.plugins_folder.exists():
            return
        
        current_files = set()
        for plugin_file in self.plugins_folder.glob("*.py"):
            # Skip __init__.py and other special files
            if plugin_file.name.startswith("_"):
                continue
            
            current_files.add(plugin_file.name)
            
            try:
                plugin = self.load_plugin(plugin_file)
                # Apply saved settings to the plugin
                if plugin and plugin_file.name in self.plugin_settings:
                    for setting_name, setting_value in self.plugin_settings[plugin_file.name].items():
                        try:
                            plugin.set_setting(setting_name, setting_value)
                        except Exception:
                            pass
                
                # If this plugin was previously active, enable it
                if plugin and plugin_file.name in self.active_plugins:
                    plugin.enabled = True
                    plugin.on_enable()
            except Exception:
                pass
        
        # Clean up active_plugins list - remove any that weren't found
        self.active_plugins = [p for p in self.active_plugins if p in self.plugins]
        
        # Update plugin_order
        # 1. Remove files that no longer exist
        self.plugin_order = [p for p in self.plugin_order if p in self.plugins]
        # 2. Add new files that aren't in the order list yet
        for filename in self.plugins:
            if filename not in self.plugin_order:
                self.plugin_order.append(filename)
        
        # Save the updated configuration
        self.save_plugins_config()

    def load_plugins_config(self):
        """Load plugin configuration from JSON file"""
        if self.plugins_config_path and self.plugins_config_path.exists():
            try:
                with open(self.plugins_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.active_plugins = config.get('active_plugins', [])
                    self.plugin_order = config.get('plugin_order', [])
                    self.plugin_settings = config.get('plugin_settings', {})
            except Exception:
                self.active_plugins = []
                self.plugin_order = []
                self.plugin_settings = {}
        else:
            self.active_plugins = []
            self.plugin_order = []
            self.plugin_settings = {}
    
    def save_plugins_config(self):
        """Save plugin configuration to JSON file"""
        if self.plugins_config_path:
            try:
                # Ensure plugin_order reflects all known plugins if empty
                if not self.plugin_order:
                    self.plugin_order = sorted(list(self.plugins.keys()))
                
                config = {
                    'active_plugins': self.active_plugins,
                    'plugin_order': self.plugin_order,
                    'plugin_settings': self.plugin_settings
                }
                
                # Ensure directory exists
                if not self.plugins_config_path.parent.exists():
                    self.plugins_config_path.parent.mkdir(parents=True, exist_ok=True)
                    
                with open(self.plugins_config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
            except Exception:
                pass
    
    def load_plugin(self, plugin_path):
        """Load a single plugin from a file path"""
        if not PLUGINS_AVAILABLE:
            return None
        
        plugin_name = plugin_path.stem
        
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Look for a 'plugin' instance or a class that inherits from TextractorPlugin
            plugin_instance = None
            
            if hasattr(module, 'plugin'):
                plugin_instance = module.plugin
            else:
                # Look for a class that inherits from TextractorPlugin
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, TextractorPlugin) and 
                        attr is not TextractorPlugin):
                        plugin_instance = attr()
                        break
            
            if plugin_instance:
                self.plugins[plugin_path.name] = plugin_instance
                return plugin_instance
                
        except Exception:
            pass
        
        return None
    
    
    def activate_plugin(self, plugin_filename):
        """Activate a plugin"""
        if plugin_filename in self.plugins and plugin_filename not in self.active_plugins:
            self.active_plugins.append(plugin_filename)
            plugin = self.plugins[plugin_filename]
            plugin.enabled = True
            plugin.on_enable()
            self.save_plugins_config()
            return True
        return False
    
    def deactivate_plugin(self, plugin_filename):
        """Deactivate a plugin"""
        if plugin_filename in self.active_plugins:
            self.active_plugins.remove(plugin_filename)
            if plugin_filename in self.plugins:
                plugin = self.plugins[plugin_filename]
                plugin.enabled = False
                plugin.on_disable()
            self.save_plugins_config()
            return True
        return False
    
    def process_text_through_plugins(self, text):
        """Process text through all active plugins"""
        if not PLUGINS_AVAILABLE:
            return text
        
        current_text = text
        
        # Determine execution order: plugin_order filtered by active state
        execution_order = [p for p in self.plugin_order if p in self.active_plugins]
        
        # Iterate over the execution order
        for plugin_filename in execution_order:
            if plugin_filename in self.plugins:
                plugin = self.plugins[plugin_filename]
                if plugin.enabled:
                    try:
                        result = plugin.process_text(current_text)
                        if result is None:
                            return None
                        current_text = result
                    except Exception:
                        pass
        
        return current_text
    
    def reset_all_plugins(self):
        """Reset state of all plugins"""
        for plugin in self.plugins.values():
            try:
                plugin.reset()
            except Exception:
                pass
    
    def open_plugins_folder(self):
        """Open the plugins folder in file explorer"""
        # Ensure the folder exists before opening
        if not self.plugins_folder.exists():
            self.plugins_folder.mkdir(parents=True, exist_ok=True)
        
        # Open the folder
        try:
            os.startfile(str(self.plugins_folder))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open plugins folder:\n{str(e)}")
    
    def refresh_plugins_list(self):
        """Refresh the plugins list in the UI"""
        if hasattr(self, 'plugins_tree'):
            self.plugins_tree.delete(*self.plugins_tree.get_children())
            
            # Ensure all loaded plugins are in plugin_order
            for filename in self.plugins:
                if filename not in self.plugin_order:
                    self.plugin_order.append(filename)
            
            # Display plugins in the order defined by plugin_order
            for filename in self.plugin_order:
                if filename in self.plugins:
                    plugin = self.plugins[filename]
                    status = "✓ Active" if filename in self.active_plugins else "○ Inactive"
                    # We store the filename in the text attribute (hidden ID) for tracking
                    self.plugins_tree.insert('', tk.END, text=filename, values=(
                        status,
                        plugin.name,
                        plugin.version,
                        plugin.description[:50] + "..." if len(plugin.description) > 50 else plugin.description
                    ), tags=('active' if filename in self.active_plugins else 'inactive',))
        
        # Update count label
        if hasattr(self, 'plugins_count_label'):
            self.plugins_count_label.config(text=f"Active: {len(self.active_plugins)} plugins")
    
    def toggle_selected_plugin(self):
        """Toggle the selected plugin's active state"""
        if not hasattr(self, 'plugins_tree'):
            return
        
        selection = self.plugins_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin to toggle.")
            return
        
        item = self.plugins_tree.item(selection[0])
        plugin_name = item['values'][1]  # Get plugin name from values
        
        # Find the plugin filename by name
        plugin_filename = None
        for filename, plugin in self.plugins.items():
            if plugin.name == plugin_name:
                plugin_filename = filename
                break
        
        if plugin_filename:
            if plugin_filename in self.active_plugins:
                self.deactivate_plugin(plugin_filename)
            else:
                self.activate_plugin(plugin_filename)
            
            self.refresh_plugins_list()
    
    def add_plugin_from_file(self):
        """Add a new plugin by copying it to the plugins folder"""
        file_path = filedialog.askopenfilename(
            title="Select Plugin File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=str(Path.home())
        )
        
        if file_path:
            source_path = Path(file_path)
            dest_path = self.plugins_folder / source_path.name
            
            try:
                # Copy the file to plugins folder
                import shutil
                shutil.copy2(source_path, dest_path)
                
                # Load the new plugin
                plugin = self.load_plugin(dest_path)
                
                if plugin:
                    # Automatically activate the new plugin
                    self.activate_plugin(dest_path.name)
                    self.refresh_plugins_list()
                    messagebox.showinfo("Success", f"Plugin '{plugin.name}' added and activated!")
                else:
                    # Remove the file if it's not a valid plugin
                    dest_path.unlink()
                    messagebox.showerror("Error", "The selected file is not a valid Textractor plugin.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add plugin:\n{str(e)}")
    
    def remove_selected_plugin(self):
        """Remove the selected plugin"""
        if not hasattr(self, 'plugins_tree'):
            return
        
        selection = self.plugins_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin to remove.")
            return
        
        item = self.plugins_tree.item(selection[0])
        plugin_name = item['values'][1]
        
        # Find the plugin filename by name
        plugin_filename = None
        for filename, plugin in self.plugins.items():
            if plugin.name == plugin_name:
                plugin_filename = filename
                break
        
        if plugin_filename:
            result = messagebox.askyesno(
                "Confirm Removal",
                f"Are you sure you want to remove the plugin '{plugin_name}'?\n\n"
                "This will delete the plugin file from the plugins folder."
            )
            
            if result:
                try:
                    # Deactivate first
                    self.deactivate_plugin(plugin_filename)
                    
                    # Remove from plugins dict
                    del self.plugins[plugin_filename]
                    
                    # Remove from plugin_order
                    if plugin_filename in self.plugin_order:
                        self.plugin_order.remove(plugin_filename)
                    
                    # Delete the file
                    plugin_path = self.plugins_folder / plugin_filename
                    if plugin_path.exists():
                        plugin_path.unlink()
                    
                    # Save the updated configuration
                    self.save_plugins_config()
                    
                    self.refresh_plugins_list()
                    messagebox.showinfo("Success", f"Plugin '{plugin_name}' has been removed.")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove plugin:\n{str(e)}")
    
    def show_plugin_context_menu(self, event):
        """Show context menu for plugin with configure option"""
        # Select the item under cursor
        item = self.plugins_tree.identify_row(event.y)
        if item:
            self.plugins_tree.selection_set(item)
            
            # Get plugin info
            item_data = self.plugins_tree.item(item)
            plugin_name = item_data['values'][1]
            
            # Find the plugin filename
            plugin_filename = None
            for filename, plugin in self.plugins.items():
                if plugin.name == plugin_name:
                    plugin_filename = filename
                    break
            
            if not plugin_filename:
                return
            
            # Check if plugin has settings
            plugin = self.plugins[plugin_filename]
            has_settings = bool(plugin.get_settings())
            
            # Create context menu
            menu = tk.Menu(self.root, tearoff=0, bg=self.colors['surface'], fg=self.colors['fg'])
            
            # Toggle active/inactive
            if plugin_filename in self.active_plugins:
                menu.add_command(label="✓ Deactivate", command=self.toggle_selected_plugin)
            else:
                menu.add_command(label="○ Activate", command=self.toggle_selected_plugin)
            
            # Configure option (only if plugin has settings)
            if has_settings:
                menu.add_separator()
                menu.add_command(label="⚙️ Configure", command=self.configure_selected_plugin)
            
            # Show menu at cursor position
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
    
    def configure_selected_plugin(self):
        """Open configuration dialog for selected plugin"""
        selection = self.plugins_tree.selection()
        if not selection:
            return
        
        item = self.plugins_tree.item(selection[0])
        plugin_name = item['values'][1]
        
        # Find the plugin filename
        plugin_filename = None
        for filename, plugin in self.plugins.items():
            if plugin.name == plugin_name:
                plugin_filename = filename
                break
        
        if not plugin_filename:
            return
        
        plugin = self.plugins[plugin_filename]
        settings = plugin.get_settings()
        
        if not settings:
            messagebox.showinfo("No Settings", f"Plugin '{plugin_name}' has no configurable settings.")
            return
        
        # Create settings dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configure {plugin_name}")
        dialog.geometry("500x400")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, style="Card.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        ttk.Label(main_frame, text=f"⚙️ {plugin_name} Settings", 
                 font=('Segoe UI', 14, 'bold'),
                 foreground=self.colors['primary']).pack(pady=(0, 15))
        
        # Settings widgets
        setting_widgets = {}
        
        for setting_name, setting_info in settings.items():
            current_value, value_type, description, *options = setting_info
            options = options[0] if options else None
            
            # Setting frame
            setting_frame = ttk.Frame(main_frame)
            setting_frame.pack(fill=tk.X, pady=10)
            
            # Label
            ttk.Label(setting_frame, text=description + ":", 
                     font=('Segoe UI', 10)).pack(anchor=tk.W, pady=(0, 5))
            
            # Widget based on type
            if value_type == 'choice' and options:
                # Dropdown
                var = tk.StringVar(value=current_value)
                combo = ttk.Combobox(setting_frame, textvariable=var, state='readonly')
                
                # Set display values
                display_values = [options.get(key, key) for key in options.keys()]
                combo['values'] = display_values
                
                # Set current selection
                if current_value in options:
                    combo.set(options[current_value])
                
                combo.pack(fill=tk.X)
                setting_widgets[setting_name] = (var, options, value_type)
                
            elif value_type == 'bool':
                var = tk.BooleanVar(value=current_value)
                check = ttk.Checkbutton(setting_frame, variable=var)
                check.pack(anchor=tk.W)
                setting_widgets[setting_name] = (var, None, value_type)
                
            elif value_type == 'int':
                var = tk.IntVar(value=current_value)
                entry = ttk.Entry(setting_frame, textvariable=var)
                entry.pack(fill=tk.X)
                setting_widgets[setting_name] = (var, None, value_type)
                
            else:  # str
                var = tk.StringVar(value=current_value)
                entry = ttk.Entry(setting_frame, textvariable=var)
                entry.pack(fill=tk.X)
                setting_widgets[setting_name] = (var, None, value_type)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        def save_settings():
            """Save the settings"""
            # Ensure plugin_settings dict has entry for this plugin
            if plugin_filename not in self.plugin_settings:
                self.plugin_settings[plugin_filename] = {}
            
            for setting_name, (var, options, value_type) in setting_widgets.items():
                if value_type == 'choice' and options:
                    # Reverse lookup: get key from display value
                    display_value = var.get()
                    actual_value = None
                    for key, display in options.items():
                        if display == display_value:
                            actual_value = key
                            break
                    if actual_value is not None:
                        plugin.set_setting(setting_name, actual_value)
                        self.plugin_settings[plugin_filename][setting_name] = actual_value
                else:
                    value = var.get()
                    plugin.set_setting(setting_name, value)
                    self.plugin_settings[plugin_filename][setting_name] = value
            
            # Save to config file
            self.save_plugins_config()
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            dialog.destroy()
        
        def cancel():
            """Close dialog without saving"""
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save", command=save_settings,
                  style="TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Cancel", command=cancel,
                  style="Secondary.TButton").pack(side=tk.LEFT)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    # ==================== END PLUGIN SYSTEM METHODS ====================
    
    # ==================== GAME PROFILES SYSTEM METHODS ====================
    
    def generate_game_id(self, pid):
        """Generate unique identifier for a game based on exe path and size"""
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            exe_size = Path(exe_path).stat().st_size
            
            # Generate unique ID from path and size
            unique_string = f"{exe_path}_{exe_size}"
            game_id = hashlib.md5(unique_string.encode()).hexdigest()
            
            return game_id, exe_path, exe_size
        except Exception:
            return None, None, None
    
    def load_game_profiles(self):
        """Load game profiles from JSON file"""
        if self.game_profiles_path and self.game_profiles_path.exists():
            try:
                with open(self.game_profiles_path, 'r', encoding='utf-8') as f:
                    self.game_profiles = json.load(f)
            except Exception:
                self.game_profiles = {}
        else:
            self.game_profiles = {}
    
    def save_game_profiles(self):
        """Save game profiles to JSON file"""
        if self.game_profiles_path:
            try:
                # Ensure directory exists
                if not self.game_profiles_path.parent.exists():
                    self.game_profiles_path.parent.mkdir(parents=True, exist_ok=True)
                    
                with open(self.game_profiles_path, 'w', encoding='utf-8') as f:
                    json.dump(self.game_profiles, f, indent=2)
            except Exception:
                pass
    
    def save_hook_profile(self, hook_id=None, hook_code=None):
        """Save current hook selection to game profile"""
        if not self.current_game_id or not self.attached_pid:
            return
        
        try:
            # Get process info
            proc = psutil.Process(self.attached_pid)
            exe_name = proc.name()
            exe_path = proc.exe()
            exe_size = Path(exe_path).stat().st_size
            arch = self.get_process_architecture(self.attached_pid)
            
            # Determine hook type and data
            text_sample = ""
            if hook_code:
                hook_type = "manual"
                hook_data = hook_code
                hook_function = "Manual Hook"
            elif hook_id and hook_id in self.hooks:
                hook_type = "auto"
                hook_data = hook_id
                hook_function = self.hooks[hook_id].get('function', 'Unknown')
                # Save text sample to help identify the correct hook later
                texts = self.hooks[hook_id].get('texts', [])
                if texts:
                    # Get first non-empty text as sample
                    for text in texts:
                        if text and text.strip():
                            text_sample = text.strip()[:100]  # First 100 chars
                            break
            else:
                return
            
            # Create or update profile
            self.game_profiles[self.current_game_id] = {
                'exe_name': exe_name,
                'exe_path': exe_path,
                'exe_size': exe_size,
                'hook_type': hook_type,
                'hook_data': hook_data,
                'hook_function': hook_function,
                'text_sample': text_sample,  # Save text sample for better matching
                'last_used': time.strftime('%Y-%m-%d %H:%M:%S'),
                'architecture': arch,
                'engine': self.current_engine  # Remember which engine was used
            }
            
            # Save to file
            self.save_game_profiles()
            
            # Show brief notification
            self.append_output(f"💾 Hook profile saved for {exe_name}\n")
            
        except Exception:
            pass
    
    def check_and_load_hook_profile(self):
        """Check if game profile exists and prepare auto-hook"""
        if not self.attached_pid:
            return
        
        # Load profiles if not already loaded
        if not self.game_profiles:
            self.load_game_profiles()
        
        # Generate game ID
        game_id, exe_path, exe_size = self.generate_game_id(self.attached_pid)
        
        if not game_id:
            return
        
        self.current_game_id = game_id
        
        # Check if profile exists
        if game_id in self.game_profiles:
            profile = self.game_profiles[game_id]
            
            # Check if we need to switch engine
            saved_engine = profile.get('engine', 'luna')
            if saved_engine != self.current_engine:
                self.append_output(f"🔄 Switching to {saved_engine} engine for this game...\n")
                # Note: Need to detach and reattach with correct engine
                # For now, just show a warning in the output
                self.append_output(f"⚠️ This game was saved with {saved_engine} engine.\n")
                self.append_output(f"   Currently using {self.current_engine}. Consider switching engines.\n\n")
            
            # Set auto-hook pending flag
            self.auto_hook_pending = True
            self.auto_hook_data = profile
            
            # Show notification
            self.append_output(f"🔍 Found saved profile for {profile['exe_name']}\n")
            self.append_output(f"⌛ Will auto-select hook: {profile['hook_function']}\n\n")
    
    def attempt_auto_hook(self):
        """Attempt to automatically select saved hook with improved matching"""
        if not self.auto_hook_pending or not self.auto_hook_data:
            return
        
        profile = self.auto_hook_data
        
        try:
            if profile['hook_type'] == 'manual':
                # Auto-attach manual hook
                hook_code = profile['hook_data']
                
                if self.cli_process and self.attached_pid:
                    command = f"{hook_code} -P{self.attached_pid}\n"
                    self.cli_process.stdin.write(command)
                    self.cli_process.stdin.flush()
                    
                    self.append_output(f"✓ Auto-attached manual hook: {hook_code}\n\n")
                    self.auto_hook_pending = False
                    self.auto_hook_data = None
                    
            elif profile['hook_type'] == 'auto':
                # Try to find the correct hook using multiple strategies
                saved_hook_id = str(profile['hook_data'])
                saved_function = profile.get('hook_function', '')
                saved_text_sample = profile.get('text_sample', '')
                
                matched_hook_id = None
                
                # Strategy 1: Try exact hook ID match first
                if saved_hook_id in self.hooks:
                    # Check if there are multiple hooks with same function name
                    hooks_with_same_function = [
                        hid for hid, hook in self.hooks.items()
                        if hook.get('function') == saved_function
                    ]
                    
                    if len(hooks_with_same_function) == 1:
                        # Only one hook with this function, safe to use
                        matched_hook_id = saved_hook_id
                    elif len(hooks_with_same_function) > 1 and saved_text_sample:
                        # Multiple hooks with same function - use text sample matching
                        best_match_id = None
                        best_match_score = 0
                        
                        for hook_id in hooks_with_same_function:
                            hook_texts = self.hooks[hook_id].get('texts', [])
                            for hook_text in hook_texts:
                                if hook_text and hook_text.strip():
                                    # Calculate similarity (simple substring match)
                                    text_clean = hook_text.strip()[:100]
                                    if saved_text_sample in text_clean or text_clean in saved_text_sample:
                                        # Strong match - text samples overlap
                                        best_match_id = hook_id
                                        best_match_score = 100
                                        break
                            if best_match_score == 100:
                                break
                        
                        if best_match_id:
                            matched_hook_id = best_match_id
                            self.append_output(f"🎯 Matched hook by text sample (multiple hooks with same function)\n")
                        else:
                            # Fallback: use saved hook ID anyway
                            matched_hook_id = saved_hook_id
                            self.append_output(f"⚠️ Multiple hooks with same function - using saved ID\n")
                    else:
                        matched_hook_id = saved_hook_id
                
                # Strategy 2: If saved ID not found, try matching by function + text sample
                if not matched_hook_id and saved_function:
                    hooks_with_function = [
                        hid for hid, hook in self.hooks.items()
                        if hook.get('function') == saved_function
                    ]
                    
                    if len(hooks_with_function) == 1:
                        matched_hook_id = hooks_with_function[0]
                        self.append_output(f"🔍 Matched hook by function name\n")
                    elif len(hooks_with_function) > 1 and saved_text_sample:
                        # Use text sample to find correct hook
                        for hook_id in hooks_with_function:
                            hook_texts = self.hooks[hook_id].get('texts', [])
                            for hook_text in hook_texts:
                                if hook_text and hook_text.strip():
                                    text_clean = hook_text.strip()[:100]
                                    if saved_text_sample in text_clean or text_clean in saved_text_sample:
                                        matched_hook_id = hook_id
                                        self.append_output(f"🎯 Matched hook by text sample\n")
                                        break
                            if matched_hook_id:
                                break
                
                # Select the matched hook
                if matched_hook_id and self.cli_process:
                    try:
                        self.cli_process.stdin.write(f"select {matched_hook_id}\n")
                        self.cli_process.stdin.flush()
                        
                        self.selected_hook_id = matched_hook_id
                        self.append_output(f"✓ Auto-selected Hook {matched_hook_id}\n")
                        self.append_output(f"Function: {saved_function}\n")
                        self.append_output("─" * 50 + "\n\n")
                        
                        self.auto_hook_pending = False
                        self.auto_hook_data = None
                        if hasattr(self, '_auto_hook_scheduled'):
                            delattr(self, '_auto_hook_scheduled')
                        
                    except Exception:
                        pass
                else:
                    # Could not find matching hook - retry if attempts remain
                    if hasattr(self, '_auto_hook_retry_count') and self._auto_hook_retry_count < 3:
                        self._auto_hook_retry_count += 1
                        self.append_output(f"🔄 Hook not found yet, retrying in 5 seconds... (Attempt {self._auto_hook_retry_count + 1}/4)\n")
                        self.root.after(5000, self.attempt_auto_hook)
                    else:
                        # All retries exhausted
                        self.append_output(f"⚠️ Could not find matching hook after multiple attempts - please select manually\n\n")
                        self.auto_hook_pending = False
                        self.auto_hook_data = None
                        if hasattr(self, '_auto_hook_scheduled'):
                            delattr(self, '_auto_hook_scheduled')
                    
        except Exception:
            pass
    
    def open_profile_manager(self):
        """Open game profile management window"""
        # Load profiles
        self.load_game_profiles()
        
        # Create profile manager window
        manager = tk.Toplevel(self.root)
        manager.title("💾 Manage Game Profiles")
        manager.geometry("900x550")
        manager.minsize(850, 500)
        manager.configure(bg=self.colors['bg'])
        manager.transient(self.root)
        manager.grab_set()
        
        # Main container
        container = ttk.Frame(manager, style="TFrame")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        
        # Title section
        title_frame = ttk.Frame(container, style="Card.TFrame", padding=15)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        title_frame.columnconfigure(0, weight=1)
        
        ttk.Label(title_frame, text="💾 Saved Game Profiles", 
                 font=('Segoe UI', 16, 'bold'),
                 foreground=self.colors['primary']).pack()
        
        ttk.Label(title_frame, text=f"Total profiles: {len(self.game_profiles)}",
                 font=('Segoe UI', 10),
                 foreground=self.colors['text_dim']).pack(pady=(5, 0))
        
        # Profile list card
        list_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        list_card.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(0, weight=1)
        
        # Create treeview with better column layout
        columns = ('game', 'engine', 'hook_type', 'hook_info', 'last_used')
        profiles_tree = ttk.Treeview(list_card, columns=columns, show='headings', height=12)
        
        # Configure headings
        profiles_tree.heading('game', text='Game')
        profiles_tree.heading('engine', text='Engine')
        profiles_tree.heading('hook_type', text='Type')
        profiles_tree.heading('hook_info', text='Hook Info')
        profiles_tree.heading('last_used', text='Last Used')
        
        # Configure columns with center alignment
        profiles_tree.column('game', width=180, anchor='center')
        profiles_tree.column('engine', width=80, anchor='center')
        profiles_tree.column('hook_type', width=80, anchor='center')
        profiles_tree.column('hook_info', width=280, anchor='center')
        profiles_tree.column('last_used', width=140, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_card, orient=tk.VERTICAL, command=profiles_tree.yview)
        profiles_tree.configure(yscrollcommand=scrollbar.set)
        
        profiles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Populate profiles
        for game_id, profile in self.game_profiles.items():
            engine_name = "🌙 Luna" if profile.get('engine', 'luna') == 'luna' else "🔧 Textractor"
            hook_type = "🔧 Manual" if profile['hook_type'] == 'manual' else "🎯 Auto"
            hook_info = profile.get('hook_data', 'Unknown')
            if profile['hook_type'] == 'auto':
                hook_function = profile.get('hook_function', 'Unknown')
                hook_info = f"ID {hook_info} - {hook_function}"
            
            profiles_tree.insert('', tk.END, text=game_id, values=(
                profile['exe_name'],
                engine_name,
                hook_type,
                hook_info,
                profile.get('last_used', 'Unknown')
            ))
        
        # Buttons frame - centered
        btn_card = ttk.Frame(container, style="Card.TFrame", padding=15)
        btn_card.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Center the buttons
        btn_container = ttk.Frame(btn_card)
        btn_container.pack(expand=True)
        
        def delete_selected():
            """Delete selected profile"""
            selection = profiles_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a profile to delete.")
                return
            
            item = profiles_tree.item(selection[0])
            game_id = profiles_tree.item(selection[0], 'text')
            game_name = item['values'][0]
            
            result = messagebox.askyesno(
                "Confirm Deletion",
                f"Delete profile for '{game_name}'?"
            )
            
            if result:
                del self.game_profiles[game_id]
                self.save_game_profiles()
                profiles_tree.delete(selection[0])
                # Update title count
                for widget in title_frame.winfo_children():
                    if isinstance(widget, ttk.Label) and 'Total profiles' in str(widget.cget('text')):
                        widget.config(text=f"Total profiles: {len(self.game_profiles)}")
                messagebox.showinfo("Success", "Profile deleted.")
        
        def launch_game():
            """Launch the selected game and auto-attach"""
            selection = profiles_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a profile to launch.")
                return
            
            item = profiles_tree.item(selection[0])
            game_id = profiles_tree.item(selection[0], 'text')
            game_name = item['values'][0]
            
            if game_id not in self.game_profiles:
                return
            
            profile = self.game_profiles[game_id]
            exe_path = profile.get('exe_path', '')
            saved_engine = profile.get('engine', 'luna')
            
            if not exe_path or not os.path.exists(exe_path):
                messagebox.showerror("Error", 
                    f"Game executable not found:\n{exe_path}\n\n"
                    "The game may have been moved or uninstalled.")
                return
            
            try:
                # Switch to the saved engine if different from current
                if saved_engine != self.current_engine:
                    self.append_output(f"🔄 Switching to {saved_engine} engine for this game...\n")
                    self.current_engine = saved_engine
                    self.engine_var.set(saved_engine)
                
                # Close the profile manager window
                manager.destroy()
                
                # Launch the game
                subprocess.Popen([exe_path], shell=True)
                
                # Show notification in output
                self.append_output(f"🚀 Launching game: {game_name}\n")
                self.append_output("⏳ Waiting for process to start...\n\n")
                
                # Start a thread to monitor and auto-attach
                def monitor_and_attach():
                    # Wait a bit for the game to start
                    time.sleep(3)
                    
                    # Try to find the process (try for up to 30 seconds)
                    max_attempts = 30
                    for attempt in range(max_attempts):
                        try:
                            # Look for process by executable path
                            for proc in psutil.process_iter(['pid', 'exe']):
                                try:
                                    proc_exe = proc.info.get('exe', '')
                                    if proc_exe and os.path.normpath(proc_exe.lower()) == os.path.normpath(exe_path.lower()):
                                        # Found the process
                                        pid = proc.info['pid']
                                        
                                        # Update UI in main thread
                                        def attach_to_game():
                                            # Check if already attached
                                            if self.attached_pid:
                                                self.append_output("⚠️ Already attached to a process. Detaching first...\n")
                                                self.detach_process()
                                                time.sleep(0.5)
                                            
                                            # Refresh process list to include the new game
                                            self.refresh_processes()
                                            
                                            # Find and select the process in the tree
                                            for tree_item in self.process_tree.get_children():
                                                tree_values = self.process_tree.item(tree_item)['values']
                                                if tree_values[0] == pid:
                                                    self.process_tree.selection_set(tree_item)
                                                    self.process_tree.see(tree_item)
                                                    break
                                            
                                            # Wait a bit to ensure the UI is updated and selection is properly set
                                            # This prevents "No Selection" errors
                                            def perform_attach():
                                                self.attach_process()
                                                self.append_output(f"✓ Game launched and attached successfully!\n")
                                                self.append_output(f"⏳ Auto-hook will be applied shortly...\n\n")
                                            
                                            # Delay attachment by 4 second to ensure UI is ready
                                            self.root.after(4000, perform_attach)
                                        
                                        self.root.after(0, attach_to_game)
                                        return
                                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                    continue
                        except Exception:
                            pass
                        
                        # Wait before next attempt
                        time.sleep(1)
                    
                    # If we get here, process was not found
                    self.root.after(0, lambda: self.append_output(
                        "⚠️ Could not find game process after 30 seconds.\n"
                        "   Please attach manually if the game is running.\n\n"
                    ))
                
                threading.Thread(target=monitor_and_attach, daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch game:\n{str(e)}")
        
        def clear_all():
            """Clear all profiles"""
            if not self.game_profiles:
                messagebox.showinfo("Info", "No profiles to clear.")
                return
            
            result = messagebox.askyesno(
                "Confirm Clear All",
                f"Delete all {len(self.game_profiles)} profiles?\n\nThis cannot be undone."
            )
            
            if result:
                self.game_profiles = {}
                self.save_game_profiles()
                profiles_tree.delete(*profiles_tree.get_children())
                # Update title count
                for widget in title_frame.winfo_children():
                    if isinstance(widget, ttk.Label) and 'Total profiles' in str(widget.cget('text')):
                        widget.config(text=f"Total profiles: 0")
                messagebox.showinfo("Success", "All profiles cleared.")
        
        ttk.Button(btn_container, text="🚀 Launch Game", 
                  command=launch_game,
                  style="TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_container, text="🗑️ Delete Selected", 
                  command=delete_selected,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_container, text="🗑️ Clear All", 
                  command=clear_all,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_container, text="✖️ Close", 
                  command=manager.destroy,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        # Center the window
        manager.update_idletasks()
        x = (manager.winfo_screenwidth() // 2) - (manager.winfo_width() // 2)
        y = (manager.winfo_screenheight() // 2) - (manager.winfo_height() // 2)
        manager.geometry(f"+{x}+{y}")
    
    # ==================== END GAME PROFILES SYSTEM METHODS ====================
    
    def setup_modern_theme(self):
        """Create a modern custom theme"""
        style = ttk.Style()
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Create custom style
        style.theme_create("modern", parent="alt", settings={
            ".": {
                "configure": {
                    "background": self.colors['bg'],
                    "foreground": self.colors['fg'],
                    "bordercolor": self.colors['border'],
                    "darkcolor": self.colors['surface'],
                    "lightcolor": self.colors['surface_light'],
                    "troughcolor": self.colors['surface'],
                    "focuscolor": self.colors['primary'],
                    "selectbackground": self.colors['primary'],
                    "selectforeground": self.colors['bg'],
                    "fieldbackground": self.colors['surface'],
                    "font": ('Segoe UI', 10),
                    "borderwidth": 0
                }
            },
            "TFrame": {
                "configure": {
                    "background": self.colors['bg']
                }
            },
            "Card.TFrame": {
                "configure": {
                    "background": self.colors['surface'],
                    "relief": "flat",
                    "borderwidth": 1
                }
            },
            "TLabel": {
                "configure": {
                    "background": self.colors['bg'],
                    "foreground": self.colors['fg'],
                    "font": ('Segoe UI', 10)
                }
            },
            "Title.TLabel": {
                "configure": {
                    "font": ('Segoe UI', 12, 'bold'),
                    "foreground": self.colors['primary']
                }
            },
            "Status.TLabel": {
                "configure": {
                    "font": ('Segoe UI', 9),
                    "padding": (10, 5)
                }
            },
            "TButton": {
                "configure": {
                    "background": self.colors['primary'],
                    "foreground": self.colors['bg'],
                    "borderwidth": 0,
                    "focuscolor": "none",
                    "padding": (20, 10),
                    "font": ('Segoe UI', 9, 'bold')
                },
                "map": {
                    "background": [("active", self.colors['accent']), ("disabled", self.colors['surface'])],
                    "foreground": [("disabled", self.colors['text_dim'])]
                }
            },
            "Secondary.TButton": {
                "configure": {
                    "background": self.colors['surface_light'],
                    "foreground": self.colors['fg'],
                    "padding": (15, 8)
                },
                "map": {
                    "background": [("active", self.colors['border'])]
                }
            },
            "Danger.TButton": {
                "configure": {
                    "background": self.colors['secondary'],
                    "foreground": self.colors['bg'],
                    "padding": (15, 8)
                },
                "map": {
                    "background": [("active", "#f5c2e7")]
                }
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": self.colors['surface'],
                    "foreground": self.colors['fg'],
                    "bordercolor": self.colors['border'],
                    "lightcolor": self.colors['surface'],
                    "darkcolor": self.colors['surface'],
                    "insertcolor": self.colors['primary'],
                    "padding": (10, 8),
                    "font": ('Segoe UI', 10)
                },
                "map": {
                    "fieldbackground": [("focus", self.colors['surface_light'])],
                    "bordercolor": [("focus", self.colors['primary'])]
                }
            },
            "Treeview": {
                "configure": {
                    "background": self.colors['surface'],
                    "foreground": self.colors['fg'],
                    "fieldbackground": self.colors['surface'],
                    "borderwidth": 0,
                    "font": ('Segoe UI', 9),
                    "rowheight": 32
                },
                "map": {
                    "background": [("selected", self.colors['primary'])],
                    "foreground": [("selected", self.colors['bg'])]
                }
            },
            "Treeview.Heading": {
                "configure": {
                    "background": self.colors['surface_light'],
                    "foreground": self.colors['accent'],
                    "borderwidth": 0,
                    "font": ('Segoe UI', 9, 'bold'),
                    "padding": (10, 8)
                },
                "map": {
                    "background": [("active", self.colors['border'])]
                }
            },
            "Vertical.TScrollbar": {
                "configure": {
                    "background": self.colors['surface'],
                    "troughcolor": self.colors['bg'],
                    "borderwidth": 0,
                    "arrowsize": 14
                },
                "map": {
                    "background": [("active", self.colors['border'])]
                }
            },
            "TCheckbutton": {
                "configure": {
                    "background": self.colors['bg'],
                    "foreground": self.colors['fg'],
                    "font": ('Segoe UI', 9),
                    "indicatorcolor": self.colors['surface_light'],
                    "indicatorrelief": "flat",
                    "borderwidth": 1,
                    "relief": "flat"
                },
                "map": {
                    "foreground": [("active", self.colors['fg']), ("disabled", self.colors['text_dim'])],
                    "background": [("active", self.colors['bg'])],
                    "indicatorcolor": [("selected", self.colors['primary']), ("active", self.colors['border'])]
                }
            }
        })
        
        style.theme_use("modern")
    
    def set_window_icon(self):
        """Set the window icon from logo.webp"""
        try:
            if self.logo_path.exists():
                # Load the webp image
                logo_img = Image.open(self.logo_path)
                # Convert to PhotoImage for tkinter
                logo_photo = ImageTk.PhotoImage(logo_img)
                # Set as window icon
                self.root.iconphoto(True, logo_photo)
                # Store reference to prevent garbage collection
                self.root._logo_photo = logo_photo
        except Exception:
            pass
        
    def setup_ui(self):
        """Create the modern GUI layout"""
        # Create a canvas with scrollbar for the entire content
        canvas = tk.Canvas(self.root, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        
        # Main container inside canvas
        main_container = ttk.Frame(canvas, style="TFrame")
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas first (scrollbar will be managed dynamically)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=(15, 0))
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=main_container, anchor="nw")
        
        # Store references for scrollbar management
        self.canvas = canvas
        self.scrollbar = scrollbar
        self.scrollbar_visible = False
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Check if scrollbar is needed
            update_scrollbar_visibility()
        
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)
            update_scrollbar_visibility()
        
        def update_scrollbar_visibility():
            # In fullscreen mode, never show scrollbar
            if self.is_fullscreen:
                if self.scrollbar_visible:
                    scrollbar.pack_forget()
                    self.scrollbar_visible = False
                return
            
            # Get the canvas and content dimensions
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                content_height = bbox[3] - bbox[1]
                canvas_height = canvas.winfo_height()
                
                # Show scrollbar only if content is larger than canvas
                if content_height > canvas_height and not self.scrollbar_visible:
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, before=canvas)
                    self.scrollbar_visible = True
                elif content_height <= canvas_height and self.scrollbar_visible:
                    scrollbar.pack_forget()
                    self.scrollbar_visible = False
        
        main_container.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_canvas_width)
        
        # Enable mousewheel scrolling only when scrollbar is visible and not in fullscreen
        def on_mousewheel(event):
            if self.scrollbar_visible and not self.is_fullscreen:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Store update function for later use
        self.update_scrollbar_visibility = update_scrollbar_visibility
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = ttk.Label(header_frame, text="✨ Sugoi Hook", 
                               font=('Segoe UI', 20, 'bold'),
                               foreground=self.colors['primary'])
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(header_frame, text="Modern Text Extraction Tool",
                                   font=('Segoe UI', 10),
                                   foreground=self.colors['text_dim'])
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Engine selection toggle
        engine_frame = ttk.Frame(header_frame)
        engine_frame.pack(side=tk.RIGHT)
        
        ttk.Label(engine_frame, text="Hook Engine:", 
                 font=('Segoe UI', 9),
                 foreground=self.colors['text_dim']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.engine_var = tk.StringVar(value=self.current_engine)
        
        engine_radio1 = ttk.Radiobutton(engine_frame, text="🌙 Hook 1 (Luna)", 
                                        variable=self.engine_var, value="luna",
                                        command=self.on_engine_change)
        engine_radio1.pack(side=tk.LEFT, padx=(0, 10))
        
        engine_radio2 = ttk.Radiobutton(engine_frame, text="🔧 Hook 2 (Textractor)", 
                                        variable=self.engine_var, value="textractor",
                                        command=self.on_engine_change)
        engine_radio2.pack(side=tk.LEFT)
        
        # Content area with grid - adjusted for better space distribution
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=0)  # Process card - fixed height
        content_frame.rowconfigure(1, weight=0)  # Hook card - fixed height
        content_frame.rowconfigure(2, weight=0)  # Plugins card - fixed height
        content_frame.rowconfigure(3, weight=1)  # Output card - expandable
        content_frame.rowconfigure(4, weight=0)  # Footer - fixed height
        
        # === PROCESS SELECTION CARD ===
        self.create_process_card(content_frame)
        
        # === HOOK SELECTION CARD ===
        self.create_hook_card(content_frame)
        
        # === PLUGINS CARD ===
        self.create_plugins_card(content_frame)
        
        # === TEXT OUTPUT CARD ===
        self.create_output_card(content_frame)
        
        # === FOOTER ===
        self.create_footer(content_frame)
        
    def create_process_card(self, parent):
        """Create the process selection card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        card.columnconfigure(0, weight=1)
        
        # Card header
        header = ttk.Frame(card)
        header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 7))
        
        ttk.Label(header, text="🎮 1. Select Process", style="Title.TLabel").pack(side=tk.LEFT)
        
        # Search and refresh
        search_frame = ttk.Frame(card)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 4))
        search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.insert(0, "🔍 Search processes...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "🔍 Search processes..." else None)
        
        ttk.Button(search_frame, text="🔄 Refresh", command=self.refresh_processes,
                  style="Secondary.TButton").grid(row=0, column=1)
        
        # Process list
        list_frame = ttk.Frame(card)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ('pid', 'arch', 'name')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=3)
        self.process_tree_default_height = 3
        self.process_tree.heading('#0', text='')
        self.process_tree.heading('pid', text='PID')
        self.process_tree.heading('arch', text='Arch')
        self.process_tree.heading('name', text='Process Name')
        
        self.process_tree.column('#0', width=self.scale(40), anchor='center', stretch=False)
        self.process_tree.column('pid', width=self.scale(70), anchor='center')
        self.process_tree.column('arch', width=self.scale(60), anchor='center')
        self.process_tree.column('name', width=self.scale(400), anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Now set up the search trace after process_tree is created
        self.search_var.trace('w', lambda *args: self.filter_processes())
        
        # Enable double-click to attach
        self.process_tree.bind('<Double-Button-1>', lambda e: self.attach_process())
        
        # Action buttons
        action_frame = ttk.Frame(card)
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(action_frame, text="● Not attached", 
                                      style="Status.TLabel",
                                      foreground=self.colors['text_dim'])
        self.status_label.pack(side=tk.LEFT)
        
        # Keep attach_btn reference for state management (hidden)
        self.attach_btn = None
        
    def create_hook_card(self, parent):
        """Create the hook selection card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        card.columnconfigure(0, weight=1)
        
        # Card header
        ttk.Label(card, text="🎯 2. Select Hook", style="Title.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 4))
        
        # Hook list
        list_frame = ttk.Frame(card)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ('id', 'function', 'preview')
        self.hook_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=3)
        self.hook_tree_default_height = 3
        self.hook_tree.heading('id', text='ID')
        self.hook_tree.heading('function', text='Function')
        self.hook_tree.heading('preview', text='Text Preview')
        
        self.hook_tree.column('id', width=self.scale(60), minwidth=self.scale(60), anchor='center', stretch=False)
        self.hook_tree.column('function', width=self.scale(200), minwidth=self.scale(150), anchor='center', stretch=False)
        self.hook_tree.column('preview', width=self.scale(500), minwidth=self.scale(300), anchor='center', stretch=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.hook_tree.yview)
        self.hook_tree.configure(yscrollcommand=scrollbar.set)
        
        self.hook_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Enable double-click to select hook
        self.hook_tree.bind('<Double-Button-1>', lambda e: self.select_hook())
        
        # Manual hook input section
        manual_hook_frame = ttk.Frame(card)
        manual_hook_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(8, 0))
        manual_hook_frame.columnconfigure(1, weight=1)
        
        ttk.Label(manual_hook_frame, text="Manual Hook:", 
                 font=('Segoe UI', 9, 'bold'),
                 foreground=self.colors['accent']).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.manual_hook_entry = ttk.Entry(manual_hook_frame)
        self.manual_hook_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.manual_hook_entry.insert(0, "e.g., HB4@0 or HS-4@12345")
        self.manual_hook_entry.bind('<FocusIn>', lambda e: self.manual_hook_entry.delete(0, tk.END) 
                                    if self.manual_hook_entry.get().startswith("e.g.,") else None)
        self.manual_hook_entry.bind('<Return>', lambda e: self.attach_manual_hook())
        
        self.attach_manual_hook_btn = ttk.Button(manual_hook_frame, text="🔗 Attach Hook", 
                                                 command=self.attach_manual_hook,
                                                 style="Secondary.TButton",
                                                 state='disabled')
        self.attach_manual_hook_btn.grid(row=0, column=2)
        
        # Help button for hook syntax
        help_btn = ttk.Button(manual_hook_frame, text="❓", 
                             command=self.show_hook_help,
                             style="Secondary.TButton",
                             width=3)
        help_btn.grid(row=0, column=3, padx=(5, 0))
        
        # Keep select_hook_btn reference for state management (hidden)
        self.select_hook_btn = None
        
    def create_plugins_card(self, parent):
        """Create the plugins management card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        card.columnconfigure(0, weight=1)
        
        # Card header
        header_frame = ttk.Frame(card)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 4))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="🔌 Plugins (optional)", style="Title.TLabel").grid(row=0, column=0, sticky=tk.W)
        
        # Plugin action buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Show active plugins count
        self.plugins_count_label = ttk.Label(btn_frame, 
                                             text=f"Active: {len(self.active_plugins)} plugins",
                                             style="Status.TLabel",
                                             foreground=self.colors['text_dim'])
        self.plugins_count_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="💾 Manage Profiles", 
                  command=self.open_profile_manager,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="📂 Open Folder", 
                  command=self.open_plugins_folder,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  command=self.reload_plugins,
                  style="Secondary.TButton").pack(side=tk.LEFT)
        
        # Plugins list
        list_frame = ttk.Frame(card)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ('status', 'name', 'version', 'description')
        self.plugins_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=3)
        self.plugins_tree.heading('status', text='Status')
        self.plugins_tree.heading('name', text='Plugin Name')
        self.plugins_tree.heading('version', text='Version')
        self.plugins_tree.heading('description', text='Description')
        
        self.plugins_tree.column('status', width=self.scale(80), minwidth=self.scale(80), anchor='center', stretch=False)
        self.plugins_tree.column('name', width=self.scale(150), minwidth=self.scale(120), anchor='center', stretch=False)
        self.plugins_tree.column('version', width=self.scale(60), minwidth=self.scale(50), anchor='center', stretch=False)
        self.plugins_tree.column('description', width=self.scale(400), minwidth=self.scale(200), anchor='center', stretch=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.plugins_tree.yview)
        self.plugins_tree.configure(yscrollcommand=scrollbar.set)
        
        self.plugins_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Enable double-click to toggle plugin
        self.plugins_tree.bind('<Double-Button-1>', lambda e: self.toggle_selected_plugin())
        
        # Enable right-click context menu
        self.plugins_tree.bind('<Button-3>', self.show_plugin_context_menu)
        
        # Enable Drag and Drop for reordering
        self.plugins_tree.bind('<ButtonPress-1>', self.on_plugin_drag_start)
        self.plugins_tree.bind('<B1-Motion>', self.on_plugin_drag_motion)
        self.plugins_tree.bind('<ButtonRelease-1>', self.on_plugin_drag_release)
        
        # Populate the plugins list
        self.refresh_plugins_list()
    
    def on_plugin_drag_start(self, event):
        """Handle start of plugin drag"""
        item = self.plugins_tree.identify_row(event.y)
        if item:
            self.drag_start_item = item
            
    def on_plugin_drag_motion(self, event):
        """Handle feedback during plugin drag"""
        # Just ensure we track the drag
        pass
    
    def on_plugin_drag_release(self, event):
        """Handle end of plugin drag (drop)"""
        if not hasattr(self, 'drag_start_item') or not self.drag_start_item:
            return
            
        target_item = self.plugins_tree.identify_row(event.y)
        if target_item and target_item != self.drag_start_item:
            try:
                # Get index of target
                target_index = self.plugins_tree.index(target_item)
                
                # Move item to the target index
                self.plugins_tree.move(self.drag_start_item, '', target_index)
                
                # Update plugin_order based on the new visual order
                new_order = []
                for item in self.plugins_tree.get_children():
                    # Get filename from hidden text attribute
                    filename = self.plugins_tree.item(item, 'text')
                    if filename:
                        new_order.append(filename)
                
                # Update stored order
                self.plugin_order = new_order
                self.save_plugins_config()
                
            except Exception:
                pass
                
        self.drag_start_item = None
    
    def reload_plugins(self):
        """Reload all plugins from the plugins folder"""
        self.plugins.clear()
        self.discover_plugins()
        self.refresh_plugins_list()
        
        # Update count label
        if hasattr(self, 'plugins_count_label'):
            self.plugins_count_label.config(text=f"Active: {len(self.active_plugins)} plugins")
    
    def create_output_card(self, parent):
        """Create the text output card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)
        
        # Card header
        header_frame = ttk.Frame(card)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Label(header_frame, text="📝 Extracted Text", style="Title.TLabel").grid(row=0, column=0, sticky=tk.W)
        
        # Action buttons
        action_frame = ttk.Frame(header_frame)
        action_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Button(action_frame, text="💾 Save to File", 
                  command=self.save_to_file,
                  style="Secondary.TButton").pack(side=tk.LEFT)
        
        # Text output frame to ensure proper scrolling
        text_frame = ttk.Frame(card)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text output with explicit scrollbar configuration
        self.output_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['primary'],
            selectbackground=self.colors['primary'],
            selectforeground=self.colors['bg'],
            font=('Consolas', 10),
            borderwidth=0,
            padx=10, pady=10,
            state='disabled',
            height=6
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_text_default_height = 6
        
    def create_footer(self, parent):
        """Create the footer with action buttons"""
        footer = ttk.Frame(parent)
        footer.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5,0))
        
        ttk.Button(footer, text="🗑️ Clear", command=self.clear_output,
                  style="Secondary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        self.detach_btn = ttk.Button(footer, text="⏹️ Detach", 
                                     command=self.detach_process, 
                                     style="Danger.TButton",
                                     state='disabled')
        self.detach_btn.pack(side=tk.LEFT)
        
        if TRAY_AVAILABLE:
            ttk.Button(footer, text="🔽 Minimize to Tray", command=self.hide_to_tray,
                      style="Secondary.TButton").pack(side=tk.RIGHT)
        
    def should_exclude_process(self, proc_name, proc_path=None):
        """
        Advanced filtering to exclude system processes and bloatware
        Returns True if process should be excluded
        """
        name_lower = proc_name.lower()
        
        # 1. Check exact executable name matches
        if name_lower in self.excluded_executables:
            return True
        
        # 2. Check if it's in a system directory
        if proc_path:
            path_lower = proc_path.lower()
            for sys_dir in self.system_dirs:
                if path_lower.startswith(sys_dir):
                    return True
        
        # 3. Check system process patterns
        for pattern in self.system_process_patterns:
            if pattern in name_lower:
                return True
        
        # 4. Check bloatware patterns
        for pattern in self.bloatware_patterns:
            if pattern in name_lower:
                return True
        
        # 5. Filter processes without window titles (likely background services)
        # This will be checked in refresh_processes
        
        return False
    
    def has_visible_window(self, pid):
        """Check if process has a visible window (heuristic for user applications)"""
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid:
                        title = win32gui.GetWindowText(hwnd)
                        # Only count windows with actual titles
                        if title and len(title) > 0:
                            windows.append((hwnd, title))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            return len(windows) > 0
        except:
            # If we can't check, assume it might be valid
            return True
    
    def get_process_icon(self, pid):
        """Extract high-quality icon from process executable"""
        if pid in self.process_icons:
            return self.process_icons[pid]
        
        try:
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            
            # Try to extract both large and small icons
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            
            # Prefer large icon for better quality, fall back to small if needed
            icon_handle = large[0] if large else (small[0] if small else None)
            
            if icon_handle:
                # Use larger icon size for better quality (32x32)
                icon_size = 32
                
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, icon_size, icon_size)
                hdc = hdc.CreateCompatibleDC()
                hdc.SelectObject(hbmp)
                
                # Draw icon with transparent background support
                hdc.DrawIcon((0, 0), icon_handle)
                
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer('RGB', (icon_size, icon_size), bmpstr, 'raw', 'BGRX', 0, 1)
                
                # Resize with high-quality resampling to scaled size for better clarity
                scaled_size = self.scale(24)
                img = img.resize((scaled_size, scaled_size), Image.Resampling.LANCZOS)
                
                # Add subtle rounded corners for modern look
                mask = Image.new('L', (scaled_size, scaled_size), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0, 0), (scaled_size-1, scaled_size-1)], radius=self.scale(3), fill=255)
                img.putalpha(mask)
                
                photo = ImageTk.PhotoImage(img)
                self.process_icons[pid] = photo
                
                # Clean up icon handles
                if large:
                    win32gui.DestroyIcon(large[0])
                if small:
                    win32gui.DestroyIcon(small[0])
                
                return photo
        except Exception as e:
            # Silently fail for processes without accessible icons
            pass
        
        return None
    
    def get_process_architecture(self, pid):
        """Determine if a process is 32-bit or 64-bit"""
        try:
            if sys.platform == 'win32':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(0x1000, False, pid)
                if handle:
                    is_wow64 = ctypes.c_bool()
                    if kernel32.IsWow64Process(handle, ctypes.byref(is_wow64)):
                        kernel32.CloseHandle(handle)
                        return "x86" if is_wow64.value else "x64"
                    kernel32.CloseHandle(handle)
        except:
            pass
        return "x86"
    
    def refresh_processes(self):
        """Refresh the list of running processes with advanced filtering"""
        self.process_tree.delete(*self.process_tree.get_children())
        self.all_processes = []
        self.process_icons.clear()
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                exe_path = proc.info.get('exe', '')
                
                # Skip very low PIDs (system processes)
                if pid < 100:
                    continue
                
                # Apply advanced filtering
                if self.should_exclude_process(name, exe_path):
                    continue
                
                # Additional heuristic: check if process has visible windows
                # This helps filter out background services and daemons
                if not self.has_visible_window(pid):
                    continue
                
                arch = self.get_process_architecture(pid)
                icon = self.get_process_icon(pid)
                self.all_processes.append((pid, arch, name, icon))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        self.filter_processes()
    
    def filter_processes(self):
        """Filter processes based on search term"""
        self.process_tree.delete(*self.process_tree.get_children())
        search_term = self.search_var.get().lower()
        if search_term == "🔍 search processes...":
            search_term = ""
        
        for pid, arch, name, icon in self.all_processes:
            if search_term in name.lower() or search_term in str(pid):
                self.process_tree.insert('', tk.END, text='', values=(pid, arch, name), 
                                        image=icon if icon else '')
    
    def attach_process(self):
        """Attach to the selected process"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a process to attach.")
            return
        
        item = self.process_tree.item(selection[0])
        pid, arch, name = item['values']
        
        # Select CLI path based on current engine
        if self.engine_var.get() == "luna":
            cli_path = self.luna_x86_path if arch == "x86" else self.luna_x64_path
            if not cli_path.exists():
                cli_path = self.luna_x86_path
        else:  # textractor
            cli_path = self.textractor_x86_path if arch == "x86" else self.textractor_x64_path
            if not cli_path.exists():
                cli_path = self.textractor_x86_path
        
        try:
            # Get the directory containing the CLI executable
            cli_dir = cli_path.parent
            
            # When running as compiled executable, we need to ensure DLLs are accessible
            # Set up environment to include the CLI directory in PATH
            env = os.environ.copy()
            if getattr(sys, 'frozen', False):
                # Add the CLI directory to PATH so DLLs can be found
                env['PATH'] = str(cli_dir) + os.pathsep + env.get('PATH', '')
            
            # Create process with CREATE_NO_WINDOW flag to hide console
            import ctypes
            CREATE_NO_WINDOW = 0x08000000
            
            self.cli_process = subprocess.Popen(
                [str(cli_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-16-le',
                errors='ignore',
                bufsize=1,
                cwd=str(cli_dir),
                env=env,
                creationflags=CREATE_NO_WINDOW
            )
            
            self.cli_process.stdin.write(f"attach -P{pid}\n")
            self.cli_process.stdin.flush()
            
            self.attached_pid = pid
            self.status_label.config(text=f"● Attached to {name}", 
                                    foreground=self.colors['success'])
            
            self.detach_btn.config(state='normal')
            self.attach_manual_hook_btn.config(state='normal')
            
            self.is_reading = True
            self.hooks.clear()
            self.hook_tree.delete(*self.hook_tree.get_children())
            
            threading.Thread(target=self.read_cli_output, daemon=True).start()
            
            self.append_output(f"✓ Attached to {name} (PID: {pid})\n")
            self.append_output("⏳ Waiting for hooks... Interact with the application.\n\n")
            
            # Check for saved game profile and prepare auto-hook
            self.check_and_load_hook_profile()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to attach:\n{str(e)}")
            self.status_label.config(text="● Attachment failed", 
                                    foreground=self.colors['secondary'])
    
    def attach_manual_hook(self):
        """Attach a manual hook using hook code"""
        if not self.attached_pid:
            messagebox.showwarning("Not Attached", "Please attach to a process first.")
            return
        
        hook_code = self.manual_hook_entry.get().strip()
        
        # Check if it's the placeholder text
        if not hook_code or hook_code.startswith("e.g.,"):
            messagebox.showwarning("Invalid Hook Code", "Please enter a valid hook code.")
            return
        
        # Basic validation of hook code format
        if not self.validate_hook_code(hook_code):
            messagebox.showwarning("Invalid Hook Code", 
                "Invalid hook code format.\n\n"
                "Hook codes should start with H or R followed by type and parameters.\n"
                "Examples:\n"
                "  HB4@0\n"
                "  HS-4@12345\n"
                "  HQ@401000:user32.dll\n\n"
                "Click the ❓ button for more information.")
            return
        
        try:
            # Send hook code to CLI
            command = f"{hook_code} -P{self.attached_pid}\n"
            self.cli_process.stdin.write(command)
            self.cli_process.stdin.flush()
            
            self.append_output(f"🔗 Manual hook attached: {hook_code}\n")
            self.append_output("⏳ Waiting for text output...\n\n")
            
            # Save manual hook to game profile
            self.save_hook_profile(hook_code=hook_code)
            
            # Clear the entry field
            self.manual_hook_entry.delete(0, tk.END)
            self.manual_hook_entry.insert(0, "e.g., HB4@0 or HS-4@12345")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to attach manual hook:\n{str(e)}")
    
    def validate_hook_code(self, hook_code):
        """Validate hook code format"""
        # Basic validation - hook codes should start with H or R
        if not hook_code:
            return False
        
        # H-codes (Hook codes) or R-codes (Read codes)
        if hook_code[0] not in ['H', 'R', 'h', 'r']:
            return False
        
        # Should contain @ symbol for address
        if '@' not in hook_code:
            return False
        
        return True
    
    def show_hook_help(self):
        """Show help dialog for hook code syntax"""
        help_text = """
HOOK CODE SYNTAX GUIDE

═══════════════════════════════════════════════════════

H-CODES (Hook Codes)
Format: H{type}{flags}{data_offset}[*deref_offset][:split_offset]@address[:module[:function]]

TYPE CHARACTERS:
  A - ANSI text, big endian, single character
  B - ANSI text, single character
  W - Unicode text, single character
  H - Unicode text with hex dump, single character
  S - ANSI string
  Q - Unicode string
  V - UTF-8 string
  M - Unicode string with hex dump

FLAGS:
  F - Full string capture
  N - No context
  <number>< - Null length specifier
  <number># - Codepage specifier
  <hex>+ - Padding bytes

EXAMPLES:
  HB4@0                    Hook at address 0, ANSI single char, offset 4
  HS-4@12345               Hook at 0x12345, ANSI string, offset -4
  HQ@401000:user32.dll     Hook in user32.dll at offset 0x401000, Unicode string
  HSN-4*0@12345            Hook with no context, ANSI string, offset -4

═══════════════════════════════════════════════════════

R-CODES (Read Codes)
Format: R{type}[null_length<][codepage#]@address

TYPE CHARACTERS:
  S - ANSI string
  Q - Unicode string
  V - UTF-8 string
  M - Unicode string with hex dump

EXAMPLES:
  RS@401000               Read ANSI string at address 0x401000
  RQ@401000               Read Unicode string at address 0x401000
  RV@402000               Read UTF-8 string at address 0x402000

═══════════════════════════════════════════════════════

TIPS:
• Use hex addresses (e.g., 0x401000 or just 401000)
• Negative offsets are allowed (e.g., -4)
• Module names are optional but helpful for portability
• Start with simple hooks (HB4@0) and adjust as needed
• Monitor the output to see if the hook captures text correctly

For more information, refer to the Textractor documentation.
"""
        
        # Create a custom dialog
        help_window = tk.Toplevel(self.root)
        help_window.title("Hook Code Syntax Help")
        help_window.geometry("700x600")
        help_window.configure(bg=self.colors['bg'])
        
        # Make it modal
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(help_window, style="Card.TFrame", padding=15)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            bg=self.colors['surface'],
            fg=self.colors['fg'],
            font=('Consolas', 9),
            borderwidth=0,
            padx=10,
            pady=10
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, help_text)
        text_widget.config(state='disabled')
        
        # Close button
        close_btn = ttk.Button(help_window, text="Close", 
                              command=help_window.destroy,
                              style="Secondary.TButton")
        close_btn.pack(pady=(0, 15))
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
    
    def on_engine_change(self):
        """Handle engine toggle change"""
        if self.attached_pid:
            # Warn user about switching engines while attached
            result = messagebox.askyesno(
                "Switch Engine?",
                f"Switching engines will detach the current process.\n\n"
                f"Continue?"
            )
            if result:
                self.detach_process()
            else:
                # Revert toggle to previous engine
                self.engine_var.set(self.current_engine)
                return
        
        # Update current engine
        self.current_engine = self.engine_var.get()
    
    def read_cli_output(self):
        """Read output from CLI process with engine-specific parsing"""
        if self.engine_var.get() == "luna":
            self.read_luna_output()
        else:
            self.read_textractor_output()
    
    def read_textractor_output(self):
        """Read and parse Textractor CLI output"""
        pattern = re.compile(r'^\[(\d+):([^:]+):([^:]+):([^:]+):([^:]+):([^:]+):([^\]]+)\] (.*)$')
        console_pattern = re.compile(r'^\[Console\] (.+)$')
        
        while self.is_reading and self.cli_process:
            try:
                line = self.cli_process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                console_match = console_pattern.match(line)
                if console_match:
                    # Process console output in background thread
                    text_to_process = f"[Console] {console_match.group(1)}\n"
                    processed_text = self.process_text_through_plugins(text_to_process)
                    if processed_text is not None:
                        self.root.after(0, self.append_output, processed_text, False)
                    continue
                
                match = pattern.match(line)
                if match:
                    hook_id = match.group(1)
                    thread_name = match.group(6)
                    text = match.group(8)
                    
                    if hook_id not in self.hooks:
                        self.hooks[hook_id] = {
                            'id': hook_id,
                            'function': thread_name,
                            'texts': []
                        }
                        self.root.after(0, self.add_hook_to_list, hook_id, thread_name)
                    
                    # Store text and update preview - even if text is empty string
                    # Only store up to 3 texts for memory efficiency
                    if len(self.hooks[hook_id]['texts']) < 3:
                        self.hooks[hook_id]['texts'].append(text)
                    
                    # Always update the preview with the latest text (even if empty)
                    # This ensures the preview updates from "Waiting for text..." to actual content
                    self.root.after(0, self.update_hook_preview, hook_id, text)
                    
                    if self.selected_hook_id and hook_id == self.selected_hook_id:
                        if text:
                            # Process text through plugins in background thread
                            processed_text = self.process_text_through_plugins(text + "\n")
                            if processed_text is not None:
                                self.root.after(0, self.append_output, processed_text, False)
                    elif not self.selected_hook_id:
                        # Process text through plugins in background thread
                        processed_text = self.process_text_through_plugins(f"[Hook {hook_id}] {text}\n")
                        if processed_text is not None:
                            self.root.after(0, self.append_output, processed_text, False)
                
            except Exception:
                break
    
    def read_luna_output(self):
        """Read and parse Luna Hook CLI output"""
        # Luna Hook CLI format: [#ID|context_info] text
        pattern = re.compile(r'^\[#(\d+)\|([^\]]+)\] (.*)$')
        console_pattern = re.compile(r'^\[Console\] (.+)$')
        
        while self.is_reading and self.cli_process:
            try:
                line = self.cli_process.stdout.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Check for console messages
                console_match = console_pattern.match(line)
                if console_match:
                    text_to_process = f"[Console] {console_match.group(1)}\n"
                    processed_text = self.process_text_through_plugins(text_to_process)
                    if processed_text is not None:
                        self.root.after(0, self.append_output, processed_text, False)
                    continue
                
                # Check for hook output
                match = pattern.match(line)
                if match:
                    hook_id = match.group(1)
                    context_info = match.group(2)
                    text = match.group(3)
                    
                    # Extract hook name from context (last part before .exe)
                    context_parts = context_info.split(':')
                    if len(context_parts) >= 2:
                        # Try to find a meaningful name from the context
                        thread_name = context_parts[-2] if len(context_parts) > 1 else context_parts[0]
                    else:
                        thread_name = "Unknown"
                    
                    if hook_id not in self.hooks:
                        self.hooks[hook_id] = {
                            'id': hook_id,
                            'function': thread_name,
                            'texts': []
                        }
                        self.root.after(0, self.add_hook_to_list, hook_id, thread_name)
                    
                    # Store text and update preview
                    if len(self.hooks[hook_id]['texts']) < 3:
                        self.hooks[hook_id]['texts'].append(text)
                    
                    self.root.after(0, self.update_hook_preview, hook_id, text)
                    
                    if self.selected_hook_id and hook_id == self.selected_hook_id:
                        if text:
                            processed_text = self.process_text_through_plugins(text + "\n")
                            if processed_text is not None:
                                self.root.after(0, self.append_output, processed_text, False)
                    elif not self.selected_hook_id:
                        processed_text = self.process_text_through_plugins(f"[Hook #{hook_id}] {text}\n")
                        if processed_text is not None:
                            self.root.after(0, self.append_output, processed_text, False)
                
            except Exception:
                break
    
    def add_hook_to_list(self, hook_id, function):
        """Add a hook to the hook list"""
        self.hook_tree.insert('', tk.END, values=(hook_id, function, "Waiting for text..."))
        
        # Check if we should auto-select this hook (with longer delay to let all hooks populate)
        # Some games insert many hooks before the correct one appears
        if self.auto_hook_pending and not hasattr(self, '_auto_hook_scheduled'):
            self._auto_hook_scheduled = True
            self._auto_hook_retry_count = 0
            self.root.after(8000, self.attempt_auto_hook)  # Wait 8 seconds for hooks to populate
    
    def update_hook_preview(self, hook_id, current_text=None):
        """Update the preview text for a hook"""
        if hook_id in self.hooks:
            # Use current_text if provided, otherwise fall back to stored texts
            if current_text:
                preview_text = ' '.join(current_text.split())
            else:
                texts = self.hooks[hook_id]['texts']
                if texts and texts[0]:
                    preview_text = ' '.join(texts[0].split())
                else:
                    preview_text = None
            
            # Format the preview
            if preview_text:
                # Limit preview to 80 characters to prevent window breaking
                if len(preview_text) > 80:
                    preview = preview_text[:80] + "..."
                else:
                    preview = preview_text
            else:
                preview = "No text yet"
            
            # Update the tree view - ensure hook_id comparison works correctly
            for item in self.hook_tree.get_children():
                item_values = self.hook_tree.item(item)['values']
                # Convert both to strings for comparison to handle type mismatches
                if str(item_values[0]) == str(hook_id):
                    self.hook_tree.item(item, values=(item_values[0], item_values[1], preview))
                    break
    
    def select_hook(self):
        """Select a hook to display its output"""
        selection = self.hook_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a hook from the list.")
            return
        
        item = self.hook_tree.item(selection[0])
        hook_id = str(item['values'][0])
        
        try:
            self.cli_process.stdin.write(f"select {hook_id}\n")
            self.cli_process.stdin.flush()
            
            self.selected_hook_id = hook_id
            self.clear_output()
            self.append_output(f"✓ Selected Hook {hook_id}\n")
            self.append_output(f"Function: {item['values'][1]}\n")
            self.append_output("─" * 50 + "\n\n")
            
            if hook_id in self.hooks and self.hooks[hook_id]['texts']:
                for text in self.hooks[hook_id]['texts']:
                    self.append_output(f"{text}\n")
                self.append_output("\n" + "─" * 50 + "\n\n")
            
            # Save this hook selection to game profile
            self.save_hook_profile(hook_id=hook_id)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select hook:\n{str(e)}")
    
    def append_output(self, text, process_plugins=True):
        """Append text to the output area with plugin filtering"""
        if process_plugins:
            # Process text through active plugins
            processed_text = self.process_text_through_plugins(text)
        else:
            processed_text = text
        
        # If plugin filtered out the text, don't display it
        if processed_text is None:
            return
        
        # Use the processed text (which may have been modified by plugins)
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, processed_text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
        
        # Update statistics
        self.update_statistics(processed_text)
        
        # Auto-copy if enabled
        if self.auto_copy_enabled.get():
            self.auto_copy_text(processed_text)
    
    
    def auto_copy_text(self, text):
        """Automatically copy new text to clipboard"""
        try:
            # Only copy non-empty, non-console text
            text_clean = text.strip()
            if text_clean and not text_clean.startswith('[Console]'):
                self.root.clipboard_clear()
                self.root.clipboard_append(text_clean)
                self.root.update()
        except Exception:
            pass
    
    def copy_to_clipboard(self):
        """Copy all extracted text to clipboard"""
        try:
            text_content = self.output_text.get(1.0, tk.END).strip()
            if not text_content:
                messagebox.showinfo("Info", "No text to copy!")
                return
            
            self.root.clipboard_clear()
            self.root.clipboard_append(text_content)
            self.root.update()
            
            # Show temporary success message
            original_text = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            self.status_label.config(text="✓ Copied to clipboard!", 
                                    foreground=self.colors['success'])
            self.root.after(2000, lambda: self.status_label.config(
                text=original_text, foreground=original_color))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard:\n{str(e)}")
    
    def save_to_file(self):
        """Save extracted text to a file"""
        from tkinter import filedialog
        try:
            text_content = self.output_text.get(1.0, tk.END).strip()
            if not text_content:
                messagebox.showinfo("Info", "No text to save!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Extracted Text"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                messagebox.showinfo("Success", f"Text saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        # Reset all plugins state
        self.reset_all_plugins()
        # Reset statistics
        self.stats = {'lines': 0, 'words': 0, 'chars': 0, 'start_time': None, 'last_update': time.time()}
    
    def detach_process(self):
        """Detach from the current process"""
        if self.cli_process:
            try:
                self.is_reading = False
                if self.attached_pid:
                    self.cli_process.stdin.write(f"detach -P{self.attached_pid}\n")
                    self.cli_process.stdin.flush()
                
                self.cli_process.terminate()
                self.cli_process.wait(timeout=2)
            except:
                self.cli_process.kill()
            
            self.cli_process = None
        
        self.attached_pid = None
        self.selected_hook_id = None
        self.hooks.clear()
        self.hook_tree.delete(*self.hook_tree.get_children())
        
        # Reset all plugins state
        self.reset_all_plugins()
        
        self.status_label.config(text="● Detached", foreground=self.colors['text_dim'])
        self.detach_btn.config(state='disabled')
        
        self.append_output("\n✓ Detached from process\n")
    
    
    def create_status_bar(self):
        """Create status bar with statistics"""
        status_frame = ttk.Frame(self.root, style="Card.TFrame", padding=(10, 5))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(5, 10))
        
        self.status_conn_label = ttk.Label(status_frame, text="● Disconnected", 
                                           style="Status.TLabel",
                                           foreground=self.colors['text_dim'])
        self.status_conn_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.status_lines_label = ttk.Label(status_frame, text="Lines: 0", style="Status.TLabel")
        self.status_lines_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.status_words_label = ttk.Label(status_frame, text="Words: 0", style="Status.TLabel")
        self.status_words_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.status_chars_label = ttk.Label(status_frame, text="Characters: 0", style="Status.TLabel")
        self.status_chars_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.status_rate_label = ttk.Label(status_frame, text="Rate: 0 c/s", style="Status.TLabel")
        self.status_rate_label.pack(side=tk.LEFT)
    
    def update_status_bar(self):
        """Update status bar with current statistics"""
        if self.attached_pid:
            conn_text = f"● Connected (PID: {self.attached_pid})"
            self.status_conn_label.config(text=conn_text, foreground=self.colors['success'])
        else:
            self.status_conn_label.config(text="● Disconnected", foreground=self.colors['text_dim'])
        
        self.status_lines_label.config(text=f"Lines: {self.stats['lines']}")
        self.status_words_label.config(text=f"Words: {self.stats['words']}")
        self.status_chars_label.config(text=f"Characters: {self.stats['chars']}")
        
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            if elapsed > 0:
                rate = self.stats['chars'] / elapsed
                self.status_rate_label.config(text=f"Rate: {rate:.1f} c/s")
        
        self.root.after(1000, self.update_status_bar)
    
    def update_statistics(self, text):
        """Update statistics when new text is added"""
        if not self.stats['start_time']:
            self.stats['start_time'] = time.time()
        
        lines = text.count('\n')
        words = len(text.split())
        chars = len(text)
        
        self.stats['lines'] += lines
        self.stats['words'] += words
        self.stats['chars'] += chars
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        if not TRAY_AVAILABLE:
            return
        
        try:
            def create_tray_icon():
                # Try to use logo.webp first, fallback to generated icon
                try:
                    if self.logo_path.exists():
                        # Load the logo
                        logo_img = Image.open(self.logo_path)
                        # Resize to appropriate tray icon size (64x64)
                        logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)
                        # Ensure it has an alpha channel
                        if logo_img.mode != 'RGBA':
                            logo_img = logo_img.convert('RGBA')
                        return logo_img
                    else:
                        raise FileNotFoundError("Logo not found")
                except Exception:
                    # Fallback: Create a simple but visible icon
                    try:
                        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(image)
                        
                        # Draw a solid rounded rectangle background
                        draw.rounded_rectangle([(4, 4), (60, 60)], radius=12, fill='#89b4fa')
                        
                        # Draw "T" letter in white - use simple drawing without font
                        # Draw a large "T" using rectangles for better visibility
                        # Vertical bar of T
                        draw.rectangle([(26, 16), (38, 48)], fill='white')
                        # Horizontal bar of T
                        draw.rectangle([(18, 16), (46, 26)], fill='white')
                        
                        return image
                    except Exception:
                        # Ultimate fallback - simple colored square
                        image = Image.new('RGBA', (64, 64), '#89b4fa')
                        return image
            
            def get_connection_status():
                """Get current connection status for menu"""
                if self.attached_pid:
                    return f"Connected (PID: {self.attached_pid})"
                return "Not Connected"
            
            def refresh_processes_from_tray(icon, item):
                """Refresh process list from system tray"""
                self.refresh_processes()
            
            def clear_output_from_tray(icon, item):
                """Clear output from system tray"""
                self.clear_output()
            
            def copy_to_clipboard_from_tray(icon, item):
                """Copy text to clipboard from system tray"""
                self.copy_to_clipboard()
            
            # Create enhanced menu with more options
            menu = pystray.Menu(
                item('Show Window', self.show_window, default=True),
                item('Hide to Tray', self.hide_to_tray),
                pystray.Menu.SEPARATOR,
                item(lambda text: get_connection_status(), None, enabled=False),
                pystray.Menu.SEPARATOR,
                item('Copy Text to Clipboard', copy_to_clipboard_from_tray),
                item('Clear Output', clear_output_from_tray),
                pystray.Menu.SEPARATOR,
                item('Refresh Processes', refresh_processes_from_tray),
                pystray.Menu.SEPARATOR,
                item('Exit', self.quit_app)
            )
            
            self.tray_icon = pystray.Icon(
                "sugoihook", 
                create_tray_icon(), 
                "Sugoi Hook - Text Extraction Tool",
                menu
            )
            
            # Set up single-click to show window
            def on_click(icon, button, time):
                """Handle tray icon clicks"""
                if button == pystray.MouseButton.Left:
                    # Left click shows the window
                    self.show_window()
            
            self.tray_icon.on_click = on_click
            
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        except Exception:
            self.tray_icon = None
            self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
    
    def show_window(self, icon=None, item=None):
        """Show the main window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_minimized_to_tray = False
        
        # Update tray icon tooltip with current status
        if TRAY_AVAILABLE and self.tray_icon:
            if self.attached_pid:
                self.tray_icon.title = f"Sugoi Hook - Connected (PID: {self.attached_pid})"
            else:
                self.tray_icon.title = "Sugoi Hook - Text Extraction Tool"
    
    def hide_to_tray(self, icon=None, item=None):
        """Hide window to system tray"""
        if TRAY_AVAILABLE:
            self.root.withdraw()
            self.is_minimized_to_tray = True
    
    def on_window_close(self):
        """Handle window close button"""
        # Save configuration on close
        self.save_plugins_config()
        
        if TRAY_AVAILABLE:
            self.hide_to_tray()
        else:
            self.quit_app()
    
    def quit_app(self, icon=None, item=None):
        """Completely quit the application"""
        # Save configuration on exit
        self.save_plugins_config()
        
        if self.cli_process:
            self.detach_process()
        if TRAY_AVAILABLE and self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        self.adjust_layout_for_fullscreen()
        return "break"
    
    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
            self.adjust_layout_for_fullscreen()
        return "break"
    
    def on_window_configure(self, event=None):
        """Handle window configuration changes"""
        # Detect if window is maximized (not fullscreen)
        if event and event.widget == self.root:
            # Check if window state changed
            self.root.after(100, self.adjust_layout_for_fullscreen)
    
    def adjust_layout_for_fullscreen(self):
        """Adjust component heights based on fullscreen/windowed mode"""
        if self.is_fullscreen:
            # In fullscreen: increase heights to fill screen, hide scrollbar
            self.process_tree.config(height=4)
            self.hook_tree.config(height=4)
            self.output_text.config(height=15)
            
            # Force scrollbar to hide
            if hasattr(self, 'update_scrollbar_visibility'):
                self.update_scrollbar_visibility()
            
            # Reset canvas scroll position to top
            if hasattr(self, 'canvas'):
                self.canvas.yview_moveto(0)
        else:
            # In windowed mode: restore default heights, allow scrollbar
            self.process_tree.config(height=self.process_tree_default_height)
            self.hook_tree.config(height=self.hook_tree_default_height)
            self.output_text.config(height=self.output_text_default_height)
            
            # Update scrollbar visibility
            if hasattr(self, 'update_scrollbar_visibility'):
                self.root.after(100, self.update_scrollbar_visibility)
    
    def on_closing(self):
        """Handle window closing"""
        # Save configuration on close
        self.save_plugins_config()
        
        if self.cli_process:
            self.detach_process()
        self.root.destroy()

def main():
    # Check if running as script and ensure admin rights
    # This enables the underlying CLI to attach to games running as admin
    is_frozen = getattr(sys, 'frozen', False)
    is_nuitka = getattr(sys, '__compiled__', False) or (
        sys.executable.lower().endswith('.exe') and 
        'python' not in os.path.basename(sys.executable).lower()
    )
    is_compiled = is_frozen or is_nuitka
    
    if not is_compiled:
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                # Re-run with admin rights
                # Use subprocess.list2cmdline to properly quote arguments
                params = subprocess.list2cmdline(sys.argv)
                
                # Use pythonw.exe if available to avoid opening a new console window
                executable = sys.executable
                if executable.lower().endswith('python.exe'):
                    pythonw = executable[:-4] + 'w.exe'
                    if os.path.exists(pythonw):
                        executable = pythonw
                
                ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
                sys.exit()
        except Exception:
            # If elevation fails or is cancelled, continue as normal user
            pass

    # Enable DPI awareness for crisp text
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = ModernTextractorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
