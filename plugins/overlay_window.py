import tkinter as tk
from plugins import TextractorPlugin
import sys

class OverlayWindowPlugin(TextractorPlugin):
    name = "Overlay Window"
    description = "Displays text in a transparent overlay window."
    version = "1.1"
    author = "Cline"

    def __init__(self):
        super().__init__()
        self.enabled = False # Disabled by default
        self.overlay = None
        self.text_widget = None
        self.drag_data = {"x": 0, "y": 0}

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
        
        # Add a close button
        close_btn = tk.Label(self.overlay, text="×", bg=bg_color, fg='#f38ba8', font=("Arial", 14, "bold"), cursor="hand2")
        close_btn.place(relx=1.0, x=-10, y=0, anchor="ne")
        close_btn.bind("<Button-1>", lambda e: self.overlay.withdraw())

        # Container for text
        text_frame = tk.Frame(self.overlay, bg=bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Use Text widget for rich formatting
        self.text_widget = tk.Text(
            text_frame,
            bg=bg_color,
            fg='#cdd6f4', # Default text color
            font=("Segoe UI", 12),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state='disabled',
            cursor="arrow"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for formatting
        self.text_widget.tag_config("original", foreground="#a6adc8", font=("Segoe UI", 10))
        self.text_widget.tag_config("translation", foreground="#89b4fa", font=("Segoe UI", 14, "bold"))
        self.text_widget.tag_config("warning", foreground="#f9e2af", font=("Segoe UI", 12, "italic"))

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
                # Try to split
                clean_text = text.strip()
                parts = clean_text.split('\n')
                
                if len(parts) >= 2:
                    # Heuristic: Last part is translation, rest is original
                    translation = parts[-1]
                    original = '\n'.join(parts[:-1])
                    
                    self.text_widget.insert(tk.END, original + "\n", "original")
                    self.text_widget.insert(tk.END, translation, "translation")
                else:
                    # Fallback
                    self.text_widget.insert(tk.END, clean_text, "original")
            
            self.text_widget.config(state='disabled')

plugin = OverlayWindowPlugin()
