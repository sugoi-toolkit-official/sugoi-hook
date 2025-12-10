"""
Remove Duplicates Plugin
========================

Filters out duplicate text that has already been seen.
Also removes inline duplicates where the same text appears twice in a row.
"""

from plugins import TextractorPlugin
from typing import Optional


class RemoveDuplicatesPlugin(TextractorPlugin):
    """
    Filters out duplicate text entries.
    
    This plugin:
    - Removes inline duplicates (same text repeated within a line)
    - Tracks all seen text and filters out any text that has been seen before
    """
    
    name = "Remove Duplicates"
    description = "Filters out text that has already been displayed"
    version = "1.0"
    author = "Sugoi Hook"
    
    def __init__(self):
        super().__init__()
        self._state['seen_texts'] = set()
        self._state['min_length'] = 10  # Minimum length for duplicate checking
    
    def remove_inline_duplicates(self, text: str) -> str:
        """
        Remove inline duplicates where the same text appears twice in a row.
        For example: "Hello world Hello world" -> "Hello world"
        """
        if not text or len(text) < 4:
            return text
        
        text_clean = text.strip()
        
        # Try to find repeated patterns
        # Check if the text is exactly doubled
        half_len = len(text_clean) // 2
        if half_len >= 3:
            first_half = text_clean[:half_len]
            second_half = text_clean[half_len:half_len*2]
            
            # Normalize for comparison (remove extra whitespace)
            first_normalized = ' '.join(first_half.split())
            second_normalized = ' '.join(second_half.split())
            
            if first_normalized == second_normalized:
                return first_half.strip()
        
        # Check for repeated patterns with some tolerance
        # Look for patterns where text repeats with possible whitespace differences
        for pattern_len in range(3, min(len(text_clean) // 2 + 1, 200)):
            pattern = text_clean[:pattern_len]
            pattern_normalized = ''.join(pattern.split())
            
            if len(pattern_normalized) < 3:
                continue
            
            # Check if the rest of the text starts with the same pattern
            rest = text_clean[pattern_len:].lstrip()
            rest_normalized = ''.join(rest.split())
            
            if rest_normalized.startswith(pattern_normalized):
                # Found a duplicate pattern, return just the first occurrence
                return pattern.strip()
        
        return text_clean
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Check if text is a duplicate and filter if so.
        Also removes inline duplicates.
        
        Args:
            text: The text to check
            
        Returns:
            The processed text if not a duplicate, None otherwise
        """
        text_clean = text.strip()
        
        if not text_clean:
            return text  # Let empty text pass through (other plugins can handle it)
        
        # First, remove inline duplicates
        text_clean = self.remove_inline_duplicates(text_clean)
        
        # Remove ALL whitespace characters for comparison
        text_normalized = ''.join(text_clean.split())
        
        # Skip very short text (less than min_length chars after normalization)
        if len(text_normalized) < self._state['min_length']:
            return text_clean + '\n' if text.endswith('\n') else text_clean
        
        # Check if this text is already seen
        if text_normalized in self._state['seen_texts']:
            return None
        
        # Check if this text is a substring of any seen text (handles overlapping chunks)
        for seen in self._state['seen_texts']:
            if text_normalized in seen or seen in text_normalized:
                return None
        
        # Add normalized text to seen texts
        self._state['seen_texts'].add(text_normalized)
        
        # Preserve the newline if original had it
        return text_clean + '\n' if text.endswith('\n') else text_clean
    
    def reset(self):
        """Reset the seen texts tracking."""
        self._state['seen_texts'] = set()
    
    def get_settings(self) -> dict:
        """Get plugin settings."""
        return {
            'min_length': (
                self._state['min_length'],
                'int',
                'Minimum text length for duplicate checking (shorter texts are ignored)'
            )
        }
    
    def set_setting(self, name: str, value) -> bool:
        """Set a plugin setting."""
        if name == 'min_length':
            try:
                self._state['min_length'] = int(value)
                return True
            except (ValueError, TypeError):
                return False
        return False


# Plugin instance for discovery
plugin = RemoveDuplicatesPlugin()
