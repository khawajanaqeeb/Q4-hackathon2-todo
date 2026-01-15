"""
NLP Agent for Todo AI Chatbot

Handles intent classification and entity extraction from user input for the Todo AI Chatbot.
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Intent(Enum):
    ADD_TODO = "ADD_TODO"
    LIST_TODOS = "LIST_TODOS"
    COMPLETE_TODO = "COMPLETE_TODO"
    DELETE_TODO = "DELETE_TODO"
    MODIFY_TODO = "MODIFY_TODO"
    SEARCH_TODOS = "SEARCH_TODOS"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"


class EntityType(Enum):
    DATE = "date"
    PRIORITY = "priority"
    CATEGORY = "category"
    NUMBER = "number"
    KEYWORD = "keyword"


class NLPResult:
    def __init__(self, intent: Intent, entities: Dict[str, str], confidence: float = 1.0):
        self.intent = intent
        self.entities = entities
        self.confidence = confidence


class NLPAgent:
    """
    Natural Language Processing Agent that handles intent classification and entity extraction.
    """

    def __init__(self):
        # Define patterns for intent classification
        # Order matters - more specific patterns should come first
        self.intent_patterns = {
            Intent.HELP: [
                r'how do (i|can i)',
                r'how can i',
                r'what can you do',
                r'\bhelp\b',
                r'assist me',
                r'help me'
            ],
            Intent.ADD_TODO: [
                r'\badd\b\s+(a\s+)?\b(todo|task)\b',
                r'\bcreate\b\s+(a\s+)?\b(todo|task)\b',
                r'\bnew\b\s+(a\s+)?\b(todo|task)\b',
                r'\bi need to\b',
                r'\badd\b(?!\s+(do|can)\s+i\s+)',  # Negative lookahead to avoid "how do I add" and "how can I add"
                r'\bcreate\b(?!\s+(do|can)\s+i\s+)'  # Negative lookahead to avoid "how do I create" and "how can I create"
            ],
            Intent.LIST_TODOS: [
                r'\b(list|show|view)\b\s+(my|all|the|these|those)?\s*(todo|task|todos|tasks)\b',
                r'\bwhat\b.*\b(todo|task)\b',
                r'\ball\b.*\b(todo|task)\b',
                r'\blist\b.*\b(todo|task)\b',
                r'\bshow\b.*\b(todo|task)\b',
                r'\bview\b.*\b(todo|task)\b',
                r'\blist\b',
                r'\bshow\b',
                r'\bview\b',
                r'what.*tasks?.*\b(do|i|have|there)\b'
            ],
            Intent.COMPLETE_TODO: [
                r'\bcomplete\b.*\b(todo|task)\b',
                r'\bfinish\b.*\b(todo|task)\b',
                r'\bdone\b.*\b(todo|task)\b',
                r'\bcomplete\b',
                r'\bfinish\b',
                r'\bmark.*\bas\b.*\bdone\b'
            ],
            Intent.DELETE_TODO: [
                r'\bdelete\b.*\b(todo|task)\b',
                r'\bremove\b.*\b(todo|task)\b',
                r'\bdelete\b',
                r'\bremove\b'
            ],
            Intent.MODIFY_TODO: [
                r'\bchange\b.*\b(todo|task)\b',
                r'\bupdate\b.*\b(todo|task)\b',
                r'\bedit\b.*\b(todo|task)\b',
                r'\bmodify\b.*\b(todo|task)\b',
                r'\b(change|update|edit|modify)\b(?!\s+(me|can you|how|what))',
                r'\bchange\b',
                r'\bupdate\b',
                r'\bedit\b',
                r'\bmodify\b'
            ],
            Intent.SEARCH_TODOS: [
                r'\bsearch\b.*\b(todo|task)\b',
                r'\bfind\b.*\b(todo|task)\b',
                r'\blook.*for\b.*\b(todo|task)\b',
                r'\bsearch\b',
                r'\bfind\b',
                r'\blook.*for\b'
            ]
        }

        # Define patterns for entity extraction
        self.entity_patterns = {
            EntityType.DATE: [
                r'\btoday\b',
                r'\btomorrow\b',
                r'\byesterday\b',
                r'\bnext week\b',
                r'\bnext month\b',
                r'\bnext year\b',
                r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
                r'(\d{4}-\d{2}-\d{2})',      # YYYY-MM-DD
            ],
            EntityType.PRIORITY: [
                r'\bhigh priority\b',
                r'\bmedium priority\b',
                r'\blow priority\b',
                r'\burgent\b',
                r'\bimportant\b',
                r'\bhigh\b',
                r'\bmedium\b',
                r'\blow\b'
            ],
            EntityType.CATEGORY: [
                r'\bwork\b',
                r'\bpersonal\b',
                r'\bshopping\b',
                r'\bhealth\b',
                r'\bfamily\b',
                r'\bhome\b'
            ],
            EntityType.NUMBER: [
                r'\b(\d+)\b',
                r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b'
            ]
        }

    def preprocess_text(self, text: str) -> str:
        """
        Normalize input text for processing
        """
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text

    def extract_entities(self, text: str) -> Dict[str, str]:
        """
        Extract named entities from the text
        """
        entities = {}

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                # Use re.search instead of re.findall for better control over captured groups
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # If there's a group in the pattern, use the matched group
                    # Otherwise, use the entire match
                    if match.groups():
                        matched_value = match.group(1)  # First captured group
                    else:
                        matched_value = match.group(0)  # Entire match

                    # Special handling for priority entities
                    if entity_type == EntityType.PRIORITY:
                        # If we have "high priority", extract just "high"
                        if 'priority' in matched_value.lower():
                            # Split and take the first word if it's a priority-related term
                            parts = matched_value.lower().split()
                            if len(parts) > 1 and parts[1] == 'priority':
                                matched_value = parts[0]  # Take just the level (high, medium, low)

                    # Store the entity if not already stored for this type
                    if entity_type.value not in entities:
                        entities[entity_type.value] = matched_value.lower()

        return entities

    def classify_intent(self, text: str) -> Tuple[Intent, float]:
        """
        Classify the intent of the input text with confidence scoring
        """
        # Check for HELP patterns first - they have the highest priority
        for pattern in self.intent_patterns[Intent.HELP]:
            if re.search(pattern, text, re.IGNORECASE):
                # If a HELP pattern matches, return HELP regardless of other matches
                return Intent.HELP, 0.5  # Default confidence for HELP

        scores = {}

        # Skip HELP since we already checked for it
        for intent, patterns in self.intent_patterns.items():
            if intent == Intent.HELP:  # Skip HELP since we already checked
                continue

            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1

            if score > 0:
                scores[intent] = score

        if not scores:
            return Intent.UNKNOWN, 0.0

        # Find the intent with the highest score
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        # Calculate confidence as a normalized score
        total_possible_matches = sum(len(patterns) for patterns in self.intent_patterns.values())
        confidence = min(best_score / total_possible_matches * 5, 1.0)  # Scale to max 1.0

        return best_intent, confidence

    def process(self, text: str) -> NLPResult:
        """
        Process the input text and return NLP result
        """
        processed_text = self.preprocess_text(text)
        intent, confidence = self.classify_intent(processed_text)
        entities = self.extract_entities(processed_text)

        return NLPResult(intent, entities, confidence)


# Example usage
if __name__ == "__main__":
    nlp_agent = NLPAgent()

    # Test examples
    test_inputs = [
        "Add a new todo to buy groceries tomorrow",
        "Show me my todos",
        "Mark the first todo as complete",
        "Delete the urgent task",
        "Update the shopping list",
        "Find tasks with work category",
        "Help me"
    ]

    for test_input in test_inputs:
        result = nlp_agent.process(test_input)
        print(f"Input: '{test_input}'")
        print(f"Intent: {result.intent}")
        print(f"Entities: {result.entities}")
        print(f"Confidence: {result.confidence:.2f}")
        print("---")