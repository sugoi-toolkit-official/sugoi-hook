"""
Hook Concatenation Plugin
==========================

Concatenates output from multiple selected hooks into a single output.
Users can select which hooks to monitor and the order in which to display their output.
"""

from plugins import TextractorPlugin
from typing import Optional
import re


class HookConcatenationPlugin(TextractorPlugin):
    """
    Concatenates text from multiple hooks into a single ordered output.
    
    This plugin:
    - Allows selecting multiple hook IDs to monitor
    - Buffers text from each selected hook
    - Outputs concatenated text in the user-specified order
    """
    
    name = "Hook Concatenation"
    description = "Concatenate output from multiple hooks in specified order"
    version = "1.0"
    author = "Sugoi Hook"
    
    def __init__(self):
        super().__init__()
        # Settings
        self._state['enabled_mode'] = False  # Whether concatenation mode is active
        self._state['num_hooks'] = 2  # Number of hooks to concatenate
        self._state['hook_ids'] = ""  # Comma-separated hook IDs in order (e.g., "1,3,2")
        
        # Runtime state
        self._state['hook_buffers'] = {}  # Store latest text for each hook: {hook_id: text}
        
        # Pattern to match hook output format: [Hook X] text or [Hook #X] text
        self._hook_pattern = re.compile(r'^\[Hook #?(\d+)\]\s*(.*)$', re.IGNORECASE)
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Process incoming text and handle hook concatenation.
        
        Args:
            text: The text to process
            
        Returns:
            - Concatenated output from all configured hooks if in concatenation mode
            - Original text if concatenation mode is disabled
            - None to filter out individual hook outputs when concatenation is active
        """
        # If concatenation mode is not enabled, pass through unchanged
        if not self._state['enabled_mode']:
            return text
        
        # Parse hook IDs from settings
        hook_ids = self._parse_hook_ids()
        if not hook_ids:
            # No valid hooks configured, pass through
            return text
        
        # Check if this text is from a hook
        text_stripped = text.strip()
        
        # Check if it's a console message - always pass through
        if text_stripped.startswith('[Console]'):
            return text
        
        # Check for hook output format: [Hook X] text or [Hook #X] text
        match = self._hook_pattern.match(text_stripped)
        
        if match:
            # Extract hook ID and actual text
            hook_id = match.group(1)
            hook_text = match.group(2).strip()
            
            # Only track if this hook is in our configured list
            if hook_id in hook_ids:
                # If this hook already has text in buffer, it means a new dialogue cycle started
                # Clear all buffers to start fresh
                if hook_id in self._state['hook_buffers']:
                    self._state['hook_buffers'] = {}
                
                # Store this hook's text
                if hook_text:  # Only store non-empty text
                    self._state['hook_buffers'][hook_id] = hook_text
                
                # Output concatenation of whatever hooks are currently in the buffer
                concatenated = self._build_concatenated_output(hook_ids)
                
                if concatenated:
                    return concatenated
                
                # No content to output
                return None
            else:
                # This hook is NOT in our configured list - filter it out completely
                return None
        else:
            # Not a hook output format
            # For safety, pass through any text that doesn't match our pattern
            return text
    
    def _parse_hook_ids(self) -> list:
        """Parse hook IDs from the settings string."""
        hook_ids_str = self._state['hook_ids'].strip()
        if not hook_ids_str:
            return []
        
        # Split by comma and clean up
        hook_ids = []
        for hook_id in hook_ids_str.split(','):
            hook_id = hook_id.strip()
            if hook_id.isdigit():
                hook_ids.append(hook_id)
        
        return hook_ids
    
    def _build_concatenated_output(self, hook_ids: list) -> str:
        """Build concatenated output from buffers in the specified order."""
        output_parts = []
        
        for hook_id in hook_ids:
            if hook_id in self._state['hook_buffers']:
                hook_text = self._state['hook_buffers'][hook_id]
                if hook_text:  # Only include non-empty text
                    output_parts.append(hook_text)
        
        if not output_parts:
            return ""
        
        # Join directly without separators to form a single continuous sentence
        # This allows Google Translate and other plugins to process it as one complete text
        concatenated = "".join(output_parts) + "\n"
        return concatenated
    
    def reset(self):
        """Reset the plugin state."""
        self._state['hook_buffers'] = {}
    
    def on_enable(self):
        """Called when plugin is enabled."""
        self.reset()
    
    def on_disable(self):
        """Called when plugin is disabled."""
        self.reset()
    
    def get_settings(self) -> dict:
        """Get plugin settings for configuration."""
        return {
            'enabled_mode': (
                self._state['enabled_mode'],
                'bool',
                'Enable hook concatenation mode'
            ),
            'num_hooks': (
                self._state['num_hooks'],
                'int_slider',
                'Number of hooks to concatenate',
                {'min': 2, 'max': 10}
            ),
            'hook_ids': (
                self._state['hook_ids'],
                'str',
                'Hook IDs (comma-separated, e.g., 1,3,2)\nOrder determines output order.\nIMPORTANT: Do NOT select any hook - leave all unselected!'
            )
        }
    
    def set_setting(self, name: str, value) -> bool:
        """Set a plugin setting."""
        if name == 'enabled_mode':
            try:
                self._state['enabled_mode'] = bool(value)
                if self._state['enabled_mode']:
                    self.reset()  # Clear buffers when enabling
                return True
            except (ValueError, TypeError):
                return False
        
        elif name == 'num_hooks':
            try:
                num_hooks = int(value)
                if 2 <= num_hooks <= 10:
                    self._state['num_hooks'] = num_hooks
                    return True
                return False
            except (ValueError, TypeError):
                return False
        
        elif name == 'hook_ids':
            try:
                # Validate that hook_ids is a comma-separated list of numbers
                hook_ids_str = str(value).strip()
                if hook_ids_str:
                    # Validate format
                    parts = [p.strip() for p in hook_ids_str.split(',')]
                    for part in parts:
                        if not part.isdigit():
                            return False
                self._state['hook_ids'] = hook_ids_str
                self.reset()  # Clear buffers when changing hook IDs
                return True
            except (ValueError, TypeError):
                return False
        
        return False


# Plugin instance for discovery
plugin = HookConcatenationPlugin()
