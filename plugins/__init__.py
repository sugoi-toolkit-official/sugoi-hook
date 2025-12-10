"""
Textractor GUI Plugin System
============================

This module provides the plugin infrastructure for Textractor GUI.
Plugins can filter, transform, or process extracted text.

To create a plugin:
1. Create a new .py file in this plugins folder
2. Inherit from TextractorPlugin base class
3. Implement the required methods

Example:
--------
from plugins import TextractorPlugin

class MyPlugin(TextractorPlugin):
    name = "My Custom Plugin"
    description = "Does something cool with text"
    version = "1.0"
    author = "Your Name"
    
    def process_text(self, text: str) -> str | None:
        # Return modified text, or None to filter it out
        return text.upper()
"""

from abc import ABC, abstractmethod
from typing import Optional


class TextractorPlugin(ABC):
    """
    Base class for all Textractor GUI plugins.
    
    Plugins can:
    - Filter out unwanted text (return None from process_text)
    - Transform text (return modified text from process_text)
    - Track state across multiple text chunks
    
    Attributes:
        name (str): Display name of the plugin
        description (str): Brief description of what the plugin does
        version (str): Plugin version
        author (str): Plugin author
        enabled (bool): Whether the plugin is currently active
    """
    
    # Plugin metadata - override these in your plugin
    name: str = "Unnamed Plugin"
    description: str = "No description provided"
    version: str = "1.0"
    author: str = "Unknown"
    
    def __init__(self):
        """Initialize the plugin. Override to add custom initialization."""
        self.enabled = True
        self._state = {}  # For plugins that need to track state
    
    @abstractmethod
    def process_text(self, text: str) -> Optional[str]:
        """
        Process incoming text.
        
        Args:
            text: The text to process
            
        Returns:
            - The processed text (can be modified)
            - None to filter out the text completely
            - Empty string to filter out but continue processing
        """
        pass
    
    def reset(self):
        """
        Reset plugin state. Called when output is cleared or process is detached.
        Override this if your plugin maintains state.
        """
        self._state = {}
    
    def on_enable(self):
        """Called when the plugin is enabled. Override for custom behavior."""
        pass
    
    def on_disable(self):
        """Called when the plugin is disabled. Override for custom behavior."""
        pass
    
    def get_settings(self) -> dict:
        """
        Get plugin settings for UI display.
        Override to provide configurable settings.
        
        Returns:
            Dictionary of setting_name: (current_value, value_type, description)
            value_type can be: 'bool', 'int', 'str', 'choice'
        """
        return {}
    
    def set_setting(self, name: str, value) -> bool:
        """
        Set a plugin setting.
        Override to handle setting changes.
        
        Args:
            name: Setting name
            value: New value
            
        Returns:
            True if setting was applied successfully
        """
        return False
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} v{self.version}>"
