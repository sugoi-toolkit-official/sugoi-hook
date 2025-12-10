"""
Remove Special Characters Plugin
================================

Filters out text that consists only of special characters,
symbols, or repeated decorative patterns.
"""

import re
from plugins import TextractorPlugin
from typing import Optional


class RemoveSpecialCharsPlugin(TextractorPlugin):
    """
    Filters out text that consists only of special characters.
    
    This plugin detects and filters:
    - Text made up entirely of punctuation/symbols
    - Decorative lines (e.g., "----", "====", "****")
    - Repeated single characters (e.g., "aaaaaaa")
    """
    
    name = "Remove Special Characters"
    description = "Filters out text consisting only of symbols or repeated characters"
    version = "1.0"
    author = "Sugoi Hook"
    
    def __init__(self):
        super().__init__()
        # Pattern for text that is only special characters/symbols
        self._special_char_pattern = re.compile(
            r'^[\s\-_=+*#@!~`\[\]{}()|\\/<>.,;:\'\"^&%$]+$'
        )
        # Pattern for same character repeated 5+ times
        self._repeated_char_pattern = re.compile(r'^(.)\1{4,}$')
        # Pattern for decorative lines (mixed repeated chars)
        self._decorative_pattern = re.compile(r'^[\-_=~*#.]{3,}$')
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Check if text is only special characters and filter if so.
        
        Args:
            text: The text to check
            
        Returns:
            The original text if it contains meaningful content, None otherwise
        """
        text_clean = text.strip()
        
        if not text_clean:
            return text  # Let empty text pass through (other plugins can handle it)
        
        # Check if text consists only of special characters/symbols
        if self._special_char_pattern.match(text_clean):
            return None
        
        # Check if text is same character repeated many times
        if self._repeated_char_pattern.match(text_clean):
            return None
        
        # Check if text is a decorative line
        if self._decorative_pattern.match(text_clean):
            return None
        
        return text
    
    def reset(self):
        """No state to reset for this plugin."""
        pass


# Plugin instance for discovery
plugin = RemoveSpecialCharsPlugin()
