"""
Remove Empty Lines Plugin
=========================

Filters out empty or whitespace-only text.
"""

from plugins import TextractorPlugin
from typing import Optional


class RemoveEmptyPlugin(TextractorPlugin):
    """
    Filters out empty or whitespace-only text entries.
    
    This is useful for cleaning up output when the hooked application
    sends empty strings or whitespace-only content.
    """
    
    name = "Remove Empty Lines"
    description = "Filters out empty or whitespace-only text"
    version = "1.0"
    author = "Sugoi Hook"
    
    def __init__(self):
        super().__init__()
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Check if text is empty and filter if so.
        
        Args:
            text: The text to check
            
        Returns:
            The original text if not empty, None otherwise
        """
        text_clean = text.strip()
        
        if not text_clean:
            return None
        
        return text
    
    def reset(self):
        """No state to reset for this plugin."""
        pass


# Plugin instance for discovery
plugin = RemoveEmptyPlugin()
