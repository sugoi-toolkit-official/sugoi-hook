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
        # Japanese / extracted newline symbols
        self._jp_newline_pattern = re.compile(
            r'(\\n|¥n|⏎|↵)'
        )
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Check if text is only special characters and filter if so.
        
        Args:
            text: The text to check
            
        Returns:
            The original text if it contains meaningful content, None otherwise
        """
        if not text:
            return text

        # Remove Japanese-style newline symbols
        text = self._jp_newline_pattern.sub('', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            return text

        if self._special_char_pattern.match(text):
            return None

        if self._repeated_char_pattern.match(text):
            return None

        if self._decorative_pattern.match(text):
            return None

        return text
    
    def reset(self):
        """No state to reset for this plugin."""
        pass


# Plugin instance for discovery
plugin = RemoveSpecialCharsPlugin()
