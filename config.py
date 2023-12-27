"""
This module provides a simple configuration management class for working with JSON configuration files.
"""

from json import dump, load

class Config:
    """
    A configuration management class for Iroha Feedback bot.

    Example usage:

        # Create a Config instance for the "config.json" file
        config = Config("config.json")

        # Set key-value pairs in the configuration
        config.set("key1", "value1")
        config.set("key2", "value2")

        # Save the configuration to the file
        config.save()
    """

    def __init__(self, config_path):
        """
        Initialize a Config instance with the path to a JSON configuration file.

        Args:
            config_path (str, pathlib.Path): The path to the JSON configuration file.
        """
        self.config_path = config_path
        self.data = {}
        self.load()

    def load(self):
        """
        Load configuration data from the specified JSON file.
        """
        with open(self.config_path, 'r', encoding='utf-8') as config_file:
            self.data = load(config_file)

    def get(self, key):
        """
        Get the value associated with a specific key from the configuration.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            Any: The value associated with the key, or None if the key is not found.
        """
        return self.data.get(key)

    def set(self, key, value):
        """
        Set a key-value pair in the configuration.

        Args:
            key (str): The key to set.
            value (Any): The value to associate with the key.
        """
        self.data[key] = value

    def save(self):
        """
        Save the current configuration data to the specified JSON file.
        """
        with open(self.config_path, 'w', encoding='utf-8') as config_file:
            dump(self.data, config_file, indent=4)
