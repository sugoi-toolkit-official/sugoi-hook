import threading
import tkinter as tk
from plugins import TextractorPlugin
import sys
import os
from pathlib import Path

# Try to import GoogleTranslator from the Translator folder
TRANSLATOR_AVAILABLE = False
try:
    # Handle both script and compiled executable modes
    is_frozen = getattr(sys, 'frozen', False)
    is_nuitka = getattr(sys, '__compiled__', False) or (
        sys.executable.lower().endswith('.exe') and 
        'python' not in os.path.basename(sys.executable).lower()
    )
    
    if is_frozen or is_nuitka:
        # Running as compiled executable
        # The Translator folder is copied to Documents/SugoiHook/Translator
        user_data_dir = Path(os.path.expanduser("~/Documents/SugoiHook"))
        translator_dir = user_data_dir / 'Translator'
        
        # Add to sys.path if not already there
        translator_dir_str = str(translator_dir)
        if translator_dir_str not in sys.path:
            sys.path.insert(0, translator_dir_str)
        
        # Also add deep_translator directory directly
        deep_translator_dir = translator_dir / 'deep_translator'
        deep_translator_dir_str = str(deep_translator_dir)
        if deep_translator_dir_str not in sys.path:
            sys.path.insert(0, deep_translator_dir_str)
    else:
        # Running as script
        base_path = Path(__file__).resolve().parent.parent
        translator_dir = base_path / 'Translator'
        
        # Add to sys.path if not already there
        translator_dir_str = str(translator_dir)
        if translator_dir_str not in sys.path:
            sys.path.insert(0, translator_dir_str)
        
        # Also add deep_translator directory directly
        deep_translator_dir = translator_dir / 'deep_translator'
        deep_translator_dir_str = str(deep_translator_dir)
        if deep_translator_dir_str not in sys.path:
            sys.path.insert(0, deep_translator_dir_str)
        
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
except Exception:
    TRANSLATOR_AVAILABLE = False

class GoogleTranslatePlugin(TextractorPlugin):
    name = "Google Translate Overlay"
    description = "Translates text using Google Translate and displays it in a transparent overlay."
    version = "1.0"
    author = "Cline"

    def __init__(self):
        super().__init__()
        self.overlay = None
        self.original_label = None
        self.translated_label = None
        self.translator = None
        self.target_lang = 'en' # Default to English
        self.source_lang = 'auto'
        self.drag_data = {"x": 0, "y": 0}

    def on_enable(self):
        if not TRANSLATOR_AVAILABLE:
            return
        
        if not self.translator:
            try:
                self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
            except Exception:
                return

        self.create_overlay()

    def on_disable(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.original_label = None
            self.translated_label = None

    def create_overlay(self):
        if self.overlay:
            return

        # Create a Toplevel window
        self.overlay = tk.Toplevel()
        self.overlay.title("Translation Overlay")
        self.overlay.geometry("800x150+100+100")
        
        # Remove window decorations (title bar, borders)
        self.overlay.overrideredirect(True)
        
        # Keep window always on top
        self.overlay.attributes('-topmost', True)
        
        # Set transparency (alpha)
        self.overlay.attributes('-alpha', 0.8)
        
        # Set background color
        bg_color = '#1e1e2e' # Dark background matching the theme
        self.overlay.configure(bg=bg_color)

        # Make it draggable
        self.overlay.bind('<Button-1>', self.start_move)
        self.overlay.bind('<B1-Motion>', self.do_move)
        
        # Add a close button (small 'x' in top right) since we have no title bar
        close_btn = tk.Label(self.overlay, text="×", bg=bg_color, fg='#f38ba8', font=("Arial", 14, "bold"), cursor="hand2")
        close_btn.place(relx=1.0, x=-10, y=0, anchor="ne")
        close_btn.bind("<Button-1>", lambda e: self.toggle_visibility())

        # Container for text
        text_frame = tk.Frame(self.overlay, bg=bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Original text label
        self.original_label = tk.Label(
            text_frame, 
            text="Waiting for text...", 
            fg='#a6adc8', # Subtext color
            bg=bg_color, 
            wraplength=760, 
            font=("Segoe UI", 10),
            justify=tk.LEFT
        )
        self.original_label.pack(fill=tk.X, anchor="w", pady=(0, 5))

        # Translated text label
        self.translated_label = tk.Label(
            text_frame, 
            text="", 
            fg='#89b4fa', # Primary color
            bg=bg_color, 
            wraplength=760, 
            font=("Segoe UI", 14, "bold"),
            justify=tk.LEFT
        )
        self.translated_label.pack(fill=tk.X, anchor="w")

    def toggle_visibility(self):
        # Just hide it, don't disable the plugin
        if self.overlay:
            self.overlay.withdraw()
            # We might want to add a way to bring it back, but for now disabling/enabling plugin works

    def start_move(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def do_move(self, event):
        deltax = event.x - self.drag_data["x"]
        deltay = event.y - self.drag_data["y"]
        x = self.overlay.winfo_x() + deltax
        y = self.overlay.winfo_y() + deltay
        self.overlay.geometry(f"+{x}+{y}")

    def process_text(self, text: str) -> str:
        if not text or not text.strip():
            return text

        if self.enabled:
            # If overlay was closed/hidden, bring it back
            if self.overlay and self.overlay.state() == 'withdrawn':
                self.overlay.deiconify()
            elif not self.overlay:
                self.create_overlay()
                
            # Update original text immediately
            self.update_overlay_original(text)
            
            # Translate in a separate thread to avoid freezing GUI
            threading.Thread(target=self.translate_and_update, args=(text,), daemon=True).start()

        return text

    def update_overlay_original(self, text):
        if self.overlay and self.original_label:
            # Truncate if too long to avoid huge window
            display_text = text[:500] + "..." if len(text) > 500 else text
            self.original_label.config(text=display_text)

    def translate_and_update(self, text):
        if not self.translator:
            return

        try:
            # Ensure text is a string and not empty
            if not isinstance(text, str) or not text.strip():
                return
            
            translated = self.translator.translate(text)

            if self.overlay and self.translated_label:
                # Use after method to update GUI from thread
                self.overlay.after(0, lambda: self.translated_label.config(text=translated))
        except Exception as e:
            if self.overlay and self.translated_label:
                self.overlay.after(0, lambda: self.translated_label.config(text=f"Error: {str(e)}"))

plugin = GoogleTranslatePlugin()
