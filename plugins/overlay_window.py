import tkinter as tk
from tkinter import font as tkfont
from plugins import TextractorPlugin
import sys
import json
from pathlib import Path

class OverlayWindowPlugin(TextractorPlugin):
    name = "Overlay Window"
    description = "Displays text in a transparent overlay window."
    version = "2.0"
    author = "Cline"

    def __init__(self):
        super().__init__()
        self.enabled = False # Disabled by default
        self.overlay = None
        self.text_widget = None
        self.drag_data = {"x": 0, "y": 0}
        
        # Default configuration
        self.config = {
            'bg_color': '#1e1e2e',
            'translation_font': 'Segoe UI',
            'translation_font_size': 14,
            'translation_bold': True,
            'translation_color': '#89b4fa',
            'original_font': 'Segoe UI',
            'original_font_size': 10,
            'original_color': '#a6adc8',
            'warning_font': 'Segoe UI',
            'warning_font_size': 12,
            'warning_italic': True,
            'warning_color': '#f9e2af',
            'window_opacity': 80,
            'close_btn_color': '#f38ba8',
            'border_color': '#585b70',
            'min_width': 400,
            'max_width': 1200,
            'min_height': 100,
            'max_height': 300,
            'default_width': 900,
            'default_height': 200
        }
        
        # Load saved configuration
        self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            config_path = Path(__file__).parent.parent / "overlay_config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
        except Exception:
            pass

    def save_config(self):
        """Save configuration to JSON file"""
        try:
            config_path = Path(__file__).parent.parent / "overlay_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def on_enable(self):
        self.create_overlay()

    def on_disable(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.text_widget = None

    def create_overlay(self):
        if self.overlay:
            return

        # Create a Toplevel window
        try:
            self.overlay = tk.Toplevel()
        except Exception:
            return

        self.overlay.title("Text Overlay")
        
        # Set min/max size constraints from config
        self.overlay.minsize(self.config['min_width'], self.config['min_height'])
        self.overlay.maxsize(self.config['max_width'], self.config['max_height'])
        
        # Initial geometry from config
        self.overlay.geometry(f"{self.config['default_width']}x{self.config['default_height']}+100+100")
        
        # Remove window decorations (title bar, borders)
        self.overlay.overrideredirect(True)
        
        # Keep window always on top
        self.overlay.attributes('-topmost', True)
        
        # Set transparency (alpha) from config
        self.overlay.attributes('-alpha', self.config['window_opacity'] / 100.0)
        
        # Set background color from config
        bg_color = self.config['bg_color']
        self.overlay.configure(bg=bg_color)

        # Make it draggable
        self.overlay.bind('<Button-1>', self.start_move)
        self.overlay.bind('<B1-Motion>', self.do_move)
        
        # Add a close button with configurable color
        close_btn = tk.Label(self.overlay, text="×", bg=bg_color, 
                            fg=self.config['close_btn_color'], 
                            font=("Arial", 14, "bold"), cursor="hand2")
        close_btn.place(relx=1.0, x=-10, y=0, anchor="ne")
        close_btn.bind("<Button-1>", lambda e: self.overlay.withdraw())

        # Container for text
        text_frame = tk.Frame(self.overlay, bg=bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Use Text widget for rich formatting
        self.text_widget = tk.Text(
            text_frame,
            bg=bg_color,
            fg=self.config['translation_color'],
            font=(self.config['translation_font'], self.config['translation_font_size']),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state='disabled',
            cursor="arrow"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for formatting with config values
        # Original text tag
        original_font_style = (self.config['original_font'], self.config['original_font_size'])
        self.text_widget.tag_config("original", 
                                   foreground=self.config['original_color'], 
                                   font=original_font_style)
        
        # Translation text tag
        translation_font_style = [self.config['translation_font'], self.config['translation_font_size']]
        if self.config['translation_bold']:
            translation_font_style.append('bold')
        self.text_widget.tag_config("translation", 
                                   foreground=self.config['translation_color'], 
                                   font=tuple(translation_font_style))
        
        # Warning text tag
        warning_font_style = [self.config['warning_font'], self.config['warning_font_size']]
        if self.config['warning_italic']:
            warning_font_style.append('italic')
        self.text_widget.tag_config("warning", 
                                   foreground=self.config['warning_color'], 
                                   font=tuple(warning_font_style))

        # Add resize grip (bottom-right corner) with configurable color
        resize_grip = tk.Label(self.overlay, text="◢", bg=bg_color, 
                             fg=self.config['border_color'], 
                             font=("Arial", 10), cursor="size_nw_se")
        resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        resize_grip.bind("<Button-1>", self.start_resize)
        resize_grip.bind("<B1-Motion>", self.do_resize)

    def start_move(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_move(self, event):
        deltax = event.x - self.drag_data["x"]
        deltay = event.y - self.drag_data["y"]
        x = self.overlay.winfo_x() + deltax
        y = self.overlay.winfo_y() + deltay
        self.overlay.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.drag_data["width"] = self.overlay.winfo_width()
        self.drag_data["height"] = self.overlay.winfo_height()
        self.drag_data["start_x"] = event.x_root
        self.drag_data["start_y"] = event.y_root

    def do_resize(self, event):
        delta_x = event.x_root - self.drag_data["start_x"]
        delta_y = event.y_root - self.drag_data["start_y"]
        
        new_width = max(self.config['min_width'], 
                       min(self.config['max_width'], 
                           self.drag_data["width"] + delta_x))
        new_height = max(self.config['min_height'], 
                        min(self.config['max_height'], 
                            self.drag_data["height"] + delta_y))
        
        self.overlay.geometry(f"{new_width}x{new_height}")

    def process_text(self, text: str) -> str:
        if not self.enabled:
            return text
            
        # Check if Google Translate plugin is enabled
        is_translator_enabled = False
        try:
            if 'google_translate' in sys.modules:
                module = sys.modules['google_translate']
                if hasattr(module, 'plugin') and module.plugin.enabled:
                    is_translator_enabled = True
        except Exception:
            pass

        display_text = text
        
        # Update overlay
        if self.overlay:
            if self.overlay.state() == 'withdrawn':
                self.overlay.after(0, self.overlay.deiconify)
            
            self.overlay.after(0, lambda t=display_text, e=is_translator_enabled: self.update_text(t, e))
        
        return text

    def update_text(self, text, is_translator_enabled):
        if self.text_widget:
            self.text_widget.config(state='normal')
            self.text_widget.delete(1.0, tk.END)
            
            if not is_translator_enabled:
                self.text_widget.insert(tk.END, "Please enable the translation plugin", "warning")
            else:
                # Handle text with translation (original + translation format)
                clean_text = text.strip()
                parts = clean_text.split('\n')
                
                if len(parts) >= 2:
                    # Heuristic: Last part is translation, rest is original
                    translation = parts[-1]
                    original = '\n'.join(parts[:-1])
                    
                    # Display translation first (top), then original (bottom)
                    self.text_widget.insert(tk.END, translation + "\n", "translation")
                    self.text_widget.insert(tk.END, original, "original")
                else:
                    # Fallback - single line, treat as original
                    self.text_widget.insert(tk.END, clean_text, "original")
            
            self.text_widget.config(state='disabled')

    def get_settings(self) -> dict:
        """Return configurable settings for the plugin"""
        # Get available fonts
        available_fonts = sorted(list(tkfont.families()))
        fonts_dict = {font: font for font in available_fonts}
        
        # Color presets
        color_presets = {
            '#1e1e2e': 'Dark Blue (Catppuccin)',
            '#282828': 'Dark Gray (Gruvbox)',
            '#000000': 'Black',
            '#1a1a1a': 'Dark Charcoal',
            '#0d1117': 'GitHub Dark',
            '#1c1c1c': 'Almost Black',
            '#2b2b2b': 'Dark Gray',
            '#ffffff': 'White',
            '#f5f5f5': 'Off White',
            '#e0e0e0': 'Light Gray',
            '#89b4fa': 'Blue (Catppuccin)',
            '#cdd6f4': 'Light Text (Catppuccin)',
            '#a6adc8': 'Dim Text (Catppuccin)',
            '#f38ba8': 'Pink (Catppuccin)',
            '#f9e2af': 'Yellow (Catppuccin)',
            '#a6e3a1': 'Green (Catppuccin)',
            '#fab387': 'Orange (Catppuccin)',
            '#f5c2e7': 'Light Pink',
            '#b4befe': 'Lavender',
            '#585b70': 'Border Gray',
            '#00ff00': 'Bright Green',
            '#ff0000': 'Red',
            '#ffff00': 'Yellow',
            '#00ffff': 'Cyan',
            '#ff00ff': 'Magenta',
        }
        
        return {
            # Window settings
            'bg_color': (
                self.config['bg_color'],
                'color',
                'Background Color',
                color_presets
            ),
            'window_opacity': (
                self.config['window_opacity'],
                'int_slider',
                'Window Opacity (%)',
                {'min': 10, 'max': 100}
            ),
            'close_btn_color': (
                self.config['close_btn_color'],
                'color',
                'Close Button Color',
                color_presets
            ),
            'border_color': (
                self.config['border_color'],
                'color',
                'Border/Grip Color',
                color_presets
            ),
            
            # Translation text settings
            'translation_font': (
                self.config['translation_font'],
                'choice',
                'Translation Font',
                fonts_dict
            ),
            'translation_font_size': (
                self.config['translation_font_size'],
                'int_slider',
                'Translation Font Size',
                {'min': 8, 'max': 32}
            ),
            'translation_bold': (
                self.config['translation_bold'],
                'bool',
                'Translation Bold',
                None
            ),
            'translation_color': (
                self.config['translation_color'],
                'color',
                'Translation Text Color',
                color_presets
            ),
            
            # Original text settings
            'original_font': (
                self.config['original_font'],
                'choice',
                'Original Text Font',
                fonts_dict
            ),
            'original_font_size': (
                self.config['original_font_size'],
                'int_slider',
                'Original Text Font Size',
                {'min': 8, 'max': 32}
            ),
            'original_color': (
                self.config['original_color'],
                'color',
                'Original Text Color',
                color_presets
            ),
            
            # Warning text settings
            'warning_font': (
                self.config['warning_font'],
                'choice',
                'Warning Font',
                fonts_dict
            ),
            'warning_font_size': (
                self.config['warning_font_size'],
                'int_slider',
                'Warning Font Size',
                {'min': 8, 'max': 32}
            ),
            'warning_italic': (
                self.config['warning_italic'],
                'bool',
                'Warning Italic',
                None
            ),
            'warning_color': (
                self.config['warning_color'],
                'color',
                'Warning Text Color',
                color_presets
            ),
            
            # Window size settings
            'min_width': (
                self.config['min_width'],
                'int',
                'Minimum Width (px)',
                None
            ),
            'max_width': (
                self.config['max_width'],
                'int',
                'Maximum Width (px)',
                None
            ),
            'min_height': (
                self.config['min_height'],
                'int',
                'Minimum Height (px)',
                None
            ),
            'max_height': (
                self.config['max_height'],
                'int',
                'Maximum Height (px)',
                None
            ),
            'default_width': (
                self.config['default_width'],
                'int',
                'Default Width (px)',
                None
            ),
            'default_height': (
                self.config['default_height'],
                'int',
                'Default Height (px)',
                None
            ),
        }

    def set_setting(self, name: str, value) -> bool:
        """Update a plugin setting"""
        if name in self.config:
            self.config[name] = value
            self.save_config()
            
            # If overlay exists, recreate it to apply changes
            if self.overlay and self.enabled:
                self.on_disable()
                self.on_enable()
            
            return True
        return False

plugin = OverlayWindowPlugin()
