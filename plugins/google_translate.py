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
    name = "Google Translate"
    description = "Translates text using Google Translate."
    version = "1.1"
    author = "Cline"

    def __init__(self):
        super().__init__()
        self.translator = None
        self.target_lang = 'en' # Default to English
        self.source_lang = 'auto'

    def on_enable(self):
        if not TRANSLATOR_AVAILABLE:
            return
        
        if not self.translator:
            try:
                self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
            except Exception:
                return

    def process_text(self, text: str) -> str:
        if not text or not text.strip():
            return text

        if self.enabled and self.translator:
            try:
                # Synchronous translation
                translated = self.translator.translate(text)
                if translated:
                    # Ensure single newline between original and translation
                    # And add double newline at the end for spacing between blocks
                    return f"{text.rstrip()}\n{translated}\n\n"
            except Exception:
                pass

        return text

plugin = GoogleTranslatePlugin()
