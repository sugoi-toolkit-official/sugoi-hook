"""
Minimum Length Filter Plugin
============================

Filters out text that is shorter than a specified minimum length.
"""

from plugins import TextractorPlugin
from typing import Optional


class MinLengthFilterPlugin(TextractorPlugin):
    """
    Filters out text that is too short.
    
    This plugin filters text based on character count (excluding whitespace).
    Useful for filtering out single characters, short fragments, or noise.
    """
    
    name = "Minimum Length Filter"
    description = "Filters out text shorter than the specified minimum length"
    version = "1.0"
    author = "Sugoi Hook"
    
    def __init__(self):
        super().__init__()
        self._state['min_length'] = 3  # Default minimum length
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Check if text meets minimum length requirement.
        
        Args:
            text: The text to check
            
        Returns:
            The original text if it meets the minimum length, None otherwise
        """
        text_clean = text.strip()
        
        if not text_clean:
            return text  # Let empty text pass through (other plugins can handle it)
        
        # Count actual characters (excluding whitespace)
        char_count = len(''.join(text_clean.split()))
        
        if char_count < self._state['min_length']:
            return None
        
        return text
    
    def reset(self):
        """Reset plugin state (keep min_length setting)."""
        min_length = self._state.get('min_length', 3)
        self._state = {'min_length': min_length}
    
    def get_settings(self) -> dict:
        """Get plugin settings."""
        return {
            'min_length': (
                self._state['min_length'],
                'int',
                'Minimum number of characters (excluding whitespace) required'
            )
        }
    
    def set_setting(self, name: str, value) -> bool:
        """Set a plugin setting."""
        if name == 'min_length':
            try:
                new_value = int(value)
                if new_value >= 1:
                    self._state['min_length'] = new_value
                    return True
            except (ValueError, TypeError):
                pass
        return False


# Plugin instance for discovery
plugin = MinLengthFilterPlugin()
