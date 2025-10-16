"""
Prompt Configuration
====================
Manages XML-based prompt configuration for system prompts and templates.
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional


class PromptConfig:
    """Manages XML-based prompt configuration"""

    def __init__(self, config_file: str = 'prompts.xml'):
        """
        Initialize prompt configuration.

        Args:
            config_file: Path to XML configuration file
        """
        self.config_file = config_file
        self.prompts = {}
        self.load_config()

    def load_config(self):
        """Load prompts from XML file, creating default if not exists"""
        if not os.path.exists(self.config_file):
            self.create_default_config()

        tree = ET.parse(self.config_file)
        root = tree.getroot()

        for prompt_elem in root.findall('prompt'):
            name = prompt_elem.get('name')
            content = prompt_elem.text.strip()
            self.prompts[name] = content

    def create_default_config(self):
        """Create default XML configuration file with common prompts"""
        root = ET.Element('prompts')

        # Add clarification prompt
        clarification = ET.SubElement(root, 'prompt', name='clarification')
        clarification.text = """
Before responding, please consider if you need any clarification about the request.
If the request is ambiguous or lacks important details, ask for clarification first.
Be specific about what information would help you provide a better response.
        """

        # Add system prompt
        system = ET.SubElement(root, 'prompt', name='system')
        system.text = """
You are a helpful AI assistant participating in a collaborative conversation.
Provide clear, accurate, and helpful responses.
        """

        # Add thinking prompt
        thinking = ET.SubElement(root, 'prompt', name='thinking')
        thinking.text = """
Think step by step about the problem before providing a solution.
Consider edge cases and potential issues.
        """

        tree = ET.ElementTree(root)
        tree.write(self.config_file, encoding='utf-8', xml_declaration=True)

    def get_prompt(self, name: str) -> Optional[str]:
        """
        Get a prompt by name.

        Args:
            name: Prompt identifier

        Returns:
            Prompt content or None if not found
        """
        return self.prompts.get(name)

    def reload_config(self):
        """Reload configuration from disk"""
        self.prompts = {}
        self.load_config()
