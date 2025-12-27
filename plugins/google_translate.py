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
        # Look for Translator folder next to the executable
        user_data_dir = Path(sys.executable).parent
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
    version = "1.2"
    author = "Cline"

    # Available languages for translation
    LANGUAGES = {
        'auto': 'Auto-detect',
        'en': 'English',
        'ja': 'Japanese',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ko': 'Korean',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ru': 'Russian',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'tr': 'Turkish',
        'pl': 'Polish',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
    }

    def __init__(self):
        super().__init__()
        self.translator = None
        self.target_lang = 'en'  # Default to English
        self.source_lang = 'auto'  # Default to auto-detect

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

        stripped_text = text.strip()
        
        # Only translate when a hook is selected
        # When no hook is selected, text is prefixed with [Hook {id}] or [Hook #{id}]
        if stripped_text.startswith('[Hook ') or stripped_text.startswith('[Hook #'):
            # No hook selected - return text without translation
            return text
        
        # Don't translate system messages and UI elements
        # Check for common system message patterns
        system_keywords = (
            'Selected Hook', 'Attached to', 'Detached', 'Waiting for', 
            'Function:', 'Manual hook', 'Process Name', 'PID:', 
            'Interact with', 'Hook at', 'Console'
        )
        
        # Check if text contains any system keywords
        if any(keyword in stripped_text for keyword in system_keywords):
            return text
        
        # Check for lines starting with emoji/symbols (system messages)
        if stripped_text and stripped_text[0] in '✓●○🎮🎯🔌📝⏳🔗⏹️🗑️💾🔄📂🔽':
            return text
        
        # Check for lines that are console messages
        if stripped_text.startswith('[Console]'):
            return text
        
        # Don't translate lines that are mostly separator characters (more than 80% separators)
        if len(stripped_text) > 3:
            separator_chars = '─═━-_'
            separator_count = sum(1 for c in stripped_text if c in separator_chars)
            if separator_count / len(stripped_text) > 0.8:
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

    def get_settings(self) -> dict:
        """Return configurable settings for the plugin"""
        if not TRANSLATOR_AVAILABLE:
            return {}
        
        # Return settings with current values
        # Format: setting_name: (current_value, value_type, description, options)
        # For 'choice' type, options is a dict of {value: display_name}
        
        # Get target languages (exclude 'auto' for target)
        target_languages = {k: v for k, v in self.LANGUAGES.items() if k != 'auto'}
        
        return {
            'source_lang': (
                self.source_lang,
                'choice',
                'Source Language',
                self.LANGUAGES
            ),
            'target_lang': (
                self.target_lang,
                'choice',
                'Target Language',
                target_languages
            )
        }

    def set_setting(self, name: str, value) -> bool:
        """Update a plugin setting"""
        if name == 'source_lang':
            if value in self.LANGUAGES or value == 'auto':
                self.source_lang = value
                # Recreate translator with new settings
                self._recreate_translator()
                return True
        elif name == 'target_lang':
            if value in self.LANGUAGES and value != 'auto':
                self.target_lang = value
                # Recreate translator with new settings
                self._recreate_translator()
                return True
        return False

    def _recreate_translator(self):
        """Recreate the translator instance with current settings"""
        if TRANSLATOR_AVAILABLE and self.enabled:
            try:
                self.translator = GoogleTranslator(source=self.source_lang, target=self.target_lang)
            except Exception:
                self.translator = None

plugin = GoogleTranslatePlugin()
