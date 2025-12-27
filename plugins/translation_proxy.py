"""
Translator++ Translation Proxy Plugin
======================================

Translates text using Translator++ Translation Proxy which supports
more than 30 types of translation endpoints (DeepL, Google, etc.).

For more information: https://dreamsavior.net
"""

import requests
from plugins import TextractorPlugin
from typing import Optional

# ============================================================================
# CONFIGURATION - Modify these constants as needed
# ============================================================================
TARGET_LANGUAGE = ""  # Target language code (e.g., "EN", "DE", "FR", "ES", "JA", "ZH"). If blank will follow Translator++ settings.
SOURCE_LANGUAGE = ""  # Source language (use "auto" for auto-detection). If blank will follow Translator++ settings.
PROXY_URL = "http://127.0.0.1:8877/v2/translate"  # Translator++ proxy endpoint
REQUEST_TIMEOUT = 10  # Timeout in seconds for translation requests
# ============================================================================


class TranslatorPlusPlusPlugin(TextractorPlugin):
    """
    Translates using Translator++ Translation Proxy.
    
    This plugin sends text to a local Translator++ Translation Proxy server
    which supports various translation backends including DeepL, Google Translate,
    and more than 30 other translation services.
    """
    
    name = "Translator++ Proxy"
    description = "Translates using Translator++ Translation Proxy (30+ endpoints)"
    version = "1.0"
    author = "Dreamsavior (dreamsavior@gmail.com / dreamsavior.net)"
    
    def __init__(self):
        super().__init__()
        self.target_lang = TARGET_LANGUAGE
        self.source_lang = SOURCE_LANGUAGE
        self.proxy_url = PROXY_URL
        self.timeout = REQUEST_TIMEOUT
        self.session = None
    
    def on_enable(self):
        """Initialize the session when the plugin is enabled."""
        if self.session is None:
            self.session = requests.Session()
    
    def on_disable(self):
        """Clean up the session when the plugin is disabled."""
        if self.session:
            self.session.close()
            self.session = None
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Translate the text using Translator++ Translation Proxy.
        
        Args:
            text: The text to translate
            
        Returns:
            The original text with translation appended, or original text if translation fails
        """
        if not text or not text.strip():
            return text
        
        if not self.enabled:
            return text
        
        # Ensure session is initialized
        if self.session is None:
            self.on_enable()
        
        try:
            # Prepare the request payload
            payload = {
                "text": [text.strip()],
                "target_lang": self.target_lang
            }
            
            # Add source language if specified
            if self.source_lang and self.source_lang.lower() != "auto":
                payload["source_lang"] = self.source_lang
            
            # Make the translation request
            response = self.session.post(
                self.proxy_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Extract translated text from response
                # The API returns translations in a "translations" array
                if "translations" in result and len(result["translations"]) > 0:
                    translated = result["translations"][0].get("text", "")
                    if translated:
                        # Return original text with translation, separated by newline
                        # Add double newline at the end for spacing between blocks
                        return f"{text.rstrip()}\n{translated}\n\n"
            
            # If translation failed, return original text
            return text
            
        except requests.exceptions.Timeout:
            # Timeout - return original text
            return text
        except requests.exceptions.ConnectionError:
            # Connection failed - proxy might not be running
            return text
        except Exception:
            # Any other error - return original text
            return text
    
    def reset(self):
        """Reset the plugin state."""
        # Close and recreate session
        if self.session:
            self.session.close()
            self.session = None


# Plugin instance for discovery
plugin = TranslatorPlusPlusPlugin()
