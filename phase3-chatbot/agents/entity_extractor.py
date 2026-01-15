"""
Entity Extractor for Todo AI Chatbot

Extracts structured entities from natural language input for the Todo AI Chatbot.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class EntityExtractor:
    """
    Extracts structured entities from natural language input.
    """

    def __init__(self):
        # Define patterns for different entity types
        self.patterns = {
            'date': [
                r'today',
                r'tomorrow',
                r'yesterday',
                r'in (\d+) days?',
                r'in (\d+) weeks?',
                r'in (\d+) months?',
                r'on \w+day',  # Monday, Tuesday, etc.
                r'on \d{1,2}/\d{1,2}(?:/\d{4})?',  # MM/DD[/YYYY]
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'next (week|month|year)',
                r'next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                r'last (monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
            ],
            'priority': [
                r'high priority',
                r'medium priority',
                r'low priority',
                r'urgent',
                r'important',
                r'critical',
                r'high',
                r'medium',
                r'low'
            ],
            'category': [
                r'work',
                r'personal',
                r'shopping',
                r'health',
                r'family',
                r'home',
                r'hobby',
                r'finance',
                r'education',
                r'entertainment'
            ],
            'number': [
                r'(\d+)',
                r'(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)'
            ],
            'keyword': [
                r'\w+'
            ]
        }

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entities from the given text.
        """
        entities = {}

        # Normalize text for processing
        normalized_text = text.lower()

        for entity_type, patterns in self.patterns.items():
            found_entities = []

            for pattern in patterns:
                matches = re.finditer(pattern, normalized_text, re.IGNORECASE)
                for match in matches:
                    # Get the full match
                    entity_value = match.group(0).strip()

                    # For patterns with capture groups (like "in 3 days"), use the captured part
                    if match.groups():
                        captured = match.group(1)  # First capture group
                        if captured:
                            entity_value = captured

                    if entity_value and entity_value not in found_entities:
                        found_entities.append(entity_value)

            if found_entities:
                entities[entity_type] = found_entities

        return entities

    def extract_dates(self, text: str) -> List[str]:
        """
        Extract date-related entities specifically.
        """
        entities = self.extract_entities(text)
        return entities.get('date', [])

    def extract_priorities(self, text: str) -> List[str]:
        """
        Extract priority-related entities specifically.
        """
        entities = self.extract_entities(text)
        return entities.get('priority', [])

    def extract_categories(self, text: str) -> List[str]:
        """
        Extract category-related entities specifically.
        """
        entities = self.extract_entities(text)
        return entities.get('category', [])

    def extract_numbers(self, text: str) -> List[str]:
        """
        Extract number-related entities specifically.
        """
        entities = self.extract_entities(text)
        return entities.get('number', [])

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keyword-related entities specifically.
        """
        entities = self.extract_entities(text)
        return entities.get('keyword', [])


# Example usage
if __name__ == "__main__":
    extractor = EntityExtractor()

    # Test examples
    test_inputs = [
        "Add a high priority task to buy groceries tomorrow",
        "Show me my work tasks",
        "Mark the first task as complete",
        "Delete the urgent task from yesterday",
        "Update the shopping list due next week",
        "Find tasks with health category"
    ]

    for test_input in test_inputs:
        print(f"Input: '{test_input}'")
        entities = extractor.extract_entities(test_input)
        print(f"Entities: {entities}")
        print("---")