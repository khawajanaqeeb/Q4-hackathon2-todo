"""
Multi-Platform Adapter Agent

Enables the Todo AI Chatbot to work across different platforms and interfaces, adapting the core functionality to various user interaction methods and display formats.
"""

import json
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class Platform(Enum):
    WEB = "web"
    MOBILE = "mobile"
    VOICE = "voice"
    DESKTOP = "desktop"
    MESSAGING = "messaging"
    SMART_DEVICE = "smart_device"


class PlatformCapabilities:
    """Describes the capabilities of a specific platform."""

    def __init__(self, supports_graphics: bool = True, supports_audio: bool = False,
                 screen_width: Optional[int] = None, screen_height: Optional[int] = None,
                 supports_rich_text: bool = True, max_input_length: int = 1000):
        self.supports_graphics = supports_graphics
        self.supports_audio = supports_audio
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.supports_rich_text = supports_rich_text
        self.max_input_length = max_input_length


class MultiPlatformAdapterAgent:
    """
    Enables the Todo AI Chatbot to work across different platforms and interfaces.
    """

    def __init__(self):
        # Define platform capabilities
        self.platform_configs = {
            Platform.WEB: PlatformCapabilities(
                supports_graphics=True,
                supports_audio=False,
                screen_width=1920,
                screen_height=1080,
                supports_rich_text=True,
                max_input_length=1000
            ),
            Platform.MOBILE: PlatformCapabilities(
                supports_graphics=True,
                supports_audio=False,
                screen_width=375,
                screen_height=667,
                supports_rich_text=True,
                max_input_length=500
            ),
            Platform.VOICE: PlatformCapabilities(
                supports_graphics=False,
                supports_audio=True,
                screen_width=None,
                screen_height=None,
                supports_rich_text=False,
                max_input_length=200
            ),
            Platform.DESKTOP: PlatformCapabilities(
                supports_graphics=True,
                supports_audio=True,
                screen_width=1920,
                screen_height=1080,
                supports_rich_text=True,
                max_input_length=1000
            ),
            Platform.MESSAGING: PlatformCapabilities(
                supports_graphics=True,
                supports_audio=False,
                screen_width=None,
                screen_height=None,
                supports_rich_text=False,
                max_input_length=500
            ),
            Platform.SMART_DEVICE: PlatformCapabilities(
                supports_graphics=False,
                supports_audio=True,
                screen_width=320,
                screen_height=240,
                supports_rich_text=False,
                max_input_length=200
            )
        }

        # Define fallback strategies for unsupported features
        self.fallback_strategies = {
            "graphics": {
                Platform.VOICE: self._convert_graphics_to_text,
                Platform.MESSAGING: self._convert_graphics_to_simple_text,
                Platform.SMART_DEVICE: self._convert_graphics_to_basic_text
            },
            "rich_text": {
                Platform.MESSAGING: self._strip_rich_text_formatting,
                Platform.VOICE: self._convert_to_speech_friendly_text
            },
            "audio": {
                Platform.WEB: self._convert_audio_to_visual_indicators,
                Platform.MOBILE: self._convert_audio_to_visual_indicators
            }
        }

    def adapt_request(self, platform: Platform, original_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify request for platform-specific requirements.
        """
        adapted_request = original_request.copy()

        # Apply platform-specific modifications
        platform_caps = self.get_platform_capabilities(platform)

        # Truncate input if it exceeds platform's max input length
        if 'message' in adapted_request and isinstance(adapted_request['message'], str):
            if len(adapted_request['message']) > platform_caps.max_input_length:
                adapted_request['message'] = adapted_request['message'][:platform_caps.max_input_length]

        # Add platform-specific metadata
        adapted_request['platform_metadata'] = {
            'platform': platform.value,
            'timestamp': datetime.now().isoformat(),
            'capabilities': {
                'supports_graphics': platform_caps.supports_graphics,
                'supports_audio': platform_caps.supports_audio,
                'supports_rich_text': platform_caps.supports_rich_text
            }
        }

        return adapted_request

    def adapt_response(self, platform: Platform, original_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for platform.
        """
        # Get platform capabilities
        platform_caps = self.get_platform_capabilities(platform)

        # Start with the original response
        adapted_response = original_response.copy()

        # Format response based on platform capabilities
        if 'message' in adapted_response and isinstance(adapted_response['message'], str):
            message = adapted_response['message']

            # Handle graphics support
            if not platform_caps.supports_graphics and '[GRAPHICS]' in message:
                message = self._convert_graphics_to_text(message)

            # Handle rich text support
            if not platform_caps.supports_rich_text:
                message = self._strip_rich_text_formatting(message)

            # Handle audio support for voice platforms
            if platform == Platform.VOICE:
                message = self._convert_to_speech_friendly_text(message)

            adapted_response['message'] = message

        # Add platform-specific formatting
        adapted_response['formatted_for'] = platform.value
        adapted_response['adaptation_timestamp'] = datetime.now().isoformat()

        return adapted_response

    def get_platform_capabilities(self, platform: Platform) -> PlatformCapabilities:
        """
        Retrieve platform features.
        """
        if platform in self.platform_configs:
            return self.platform_configs[platform]
        else:
            # Return default capabilities if platform is unknown
            return PlatformCapabilities()

    def initialize_platform_interface(self, platform: Platform) -> Dict[str, Any]:
        """
        Set up platform-specific handlers.
        """
        capabilities = self.get_platform_capabilities(platform)

        return {
            'platform': platform.value,
            'capabilities': {
                'supports_graphics': capabilities.supports_graphics,
                'supports_audio': capabilities.supports_audio,
                'screen_dimensions': {
                    'width': capabilities.screen_width,
                    'height': capabilities.screen_height
                } if capabilities.screen_width and capabilities.screen_height else None,
                'supports_rich_text': capabilities.supports_rich_text,
                'max_input_length': capabilities.max_input_length
            },
            'initialization_timestamp': datetime.now().isoformat()
        }

    def synchronize_state(self, platform: Platform, user_id: str) -> Dict[str, Any]:
        """
        Sync user state across platforms.
        """
        # In a real implementation, this would sync state with a central store
        # For now, return a mock synchronization result
        return {
            'user_id': user_id,
            'platform': platform.value,
            'sync_status': 'success',
            'last_synced': datetime.now().isoformat(),
            'synchronized_data': {
                'active_todos_count': 5,  # Example count
                'last_interaction': '2023-12-20T10:30:00Z',
                'preferences': {
                    'notification_enabled': True,
                    'theme': 'light'
                }
            }
        }

    def handle_platform_event(self, platform: Platform, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process platform-specific events.
        """
        event_type = event.get('type', 'unknown')
        event_data = event.get('data', {})

        # Process event based on platform
        result = {
            'event_type': event_type,
            'platform': platform.value,
            'processed_at': datetime.now().isoformat(),
            'status': 'processed'
        }

        # Add platform-specific processing
        if event_type == 'screen_resize' and platform in [Platform.WEB, Platform.DESKTOP, Platform.MOBILE]:
            result['action'] = 'adjust_layout'
            result['new_dimensions'] = event_data.get('dimensions', {})
        elif event_type == 'voice_input' and platform == Platform.VOICE:
            result['action'] = 'process_speech'
            result['transcript'] = event_data.get('transcript', '')
        elif event_type == 'touch_gesture' and platform in [Platform.MOBILE, Platform.SMART_DEVICE]:
            result['action'] = 'interpret_gesture'
            result['gesture'] = event_data.get('gesture', 'tap')

        return result

    def validate_platform_compatibility(self, platform: Platform, feature: str) -> bool:
        """
        Check feature support.
        """
        if platform not in self.platform_configs:
            return False

        capabilities = self.platform_configs[platform]

        # Check if feature is supported on platform
        if feature == 'graphics':
            return capabilities.supports_graphics
        elif feature == 'audio':
            return capabilities.supports_audio
        elif feature == 'rich_text':
            return capabilities.supports_rich_text
        else:
            # For unknown features, assume they're supported
            return True

    def _convert_graphics_to_text(self, content: str) -> str:
        """Convert graphical content to text representation."""
        # Replace graphical elements with text equivalents
        conversions = {
            '[BUTTON_ADD]': '(Button: Add)',
            '[BUTTON_DELETE]': '(Button: Delete)',
            '[PROGRESS_BAR]': '[Progress: XXXXXXXXXX]',
            '[CHECKBOX]': '[ ]',
            '[CHECKED_BOX]': '[X]'
        }

        for graphic, text_equiv in conversions.items():
            content = content.replace(graphic, text_equiv)

        return content

    def _convert_graphics_to_simple_text(self, content: str) -> str:
        """Convert graphical content to simple text for messaging platforms."""
        # Strip out most graphical elements for messaging platforms
        content = content.replace('[BUTTON_ADD]', 'ADD')
        content = content.replace('[BUTTON_DELETE]', 'DELETE')
        content = content.replace('[PROGRESS_BAR]', 'PROGRESS')
        content = content.replace('[CHECKBOX]', '[ ]')
        content = content.replace('[CHECKED_BOX]', '[X]')
        return content

    def _convert_graphics_to_basic_text(self, content: str) -> str:
        """Convert graphical content to basic text for smart devices."""
        # Very simplified conversion for devices with minimal display
        content = content.replace('[BUTTON_ADD]', '+')
        content = content.replace('[BUTTON_DELETE]', '-')
        content = content.replace('[PROGRESS_BAR]', '...')
        content = content.replace('[CHECKBOX]', 'O')
        content = content.replace('[CHECKED_BOX]', 'X')
        return content

    def _strip_rich_text_formatting(self, content: str) -> str:
        """Strip rich text formatting for platforms that don't support it."""
        # Remove markdown-style formatting
        import re
        # Remove bold, italic, headers
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # Italic
        content = re.sub(r'__(.*?)__', r'\1', content)      # Bold
        content = re.sub(r'_(.*?)_', r'\1', content)        # Italic
        content = re.sub(r'#{1,6}\s*(.*?)(?=\n|$)', r'\1', content)  # Headers

        # Remove links
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)

        return content.strip()

    def _convert_to_speech_friendly_text(self, content: str) -> str:
        """Convert text to be more suitable for text-to-speech."""
        # Replace abbreviations with full words
        conversions = {
            'todo': 'to do',
            'btn': 'button',
            'msg': 'message',
            '#': 'number ',
            '@': 'at '
        }

        content = content.lower()
        for abbr, full_word in conversions.items():
            content = content.replace(abbr, full_word)

        # Remove extra punctuation that doesn't read well aloud
        import re
        content = re.sub(r'[^\w\s]', ' ', content)

        return content.strip()

    def _convert_audio_to_visual_indicators(self, content: str) -> str:
        """Convert audio-centric content to visual indicators."""
        # Replace audio cues with visual equivalents
        content = content.replace('[BEEP]', '[NOTIFICATION]')
        content = content.replace('[RING]', '[ALERT]')
        content = content.replace('[VOICE_MESSAGE]', '[AUDIO_MESSAGE]')
        return content

    def get_available_platforms(self) -> List[Platform]:
        """Get list of all supported platforms."""
        return list(self.platform_configs.keys())

    def get_platform_specific_formatting(self, platform: Platform, content_type: str, content: Any) -> Any:
        """
        Get platform-specific formatting for specific content types.
        """
        if platform == Platform.VOICE and content_type == 'list':
            # For voice platforms, convert lists to numbered verbal format
            if isinstance(content, list):
                formatted_list = []
                for i, item in enumerate(content, 1):
                    if isinstance(item, dict):
                        item_text = item.get('content', str(item))
                    else:
                        item_text = str(item)
                    formatted_list.append(f"{i}. {item_text}")
                return formatted_list
            else:
                return content

        return content


# Example usage
if __name__ == "__main__":
    # Initialize the multi-platform adapter agent
    adapter = MultiPlatformAdapterAgent()

    # Example request adaptation
    original_request = {
        'user_id': 'user123',
        'message': 'Add a new task to buy groceries [BUTTON_ADD]',
        'timestamp': datetime.now().isoformat()
    }

    # Adapt for different platforms
    web_request = adapter.adapt_request(Platform.WEB, original_request)
    mobile_request = adapter.adapt_request(Platform.MOBILE, original_request)
    voice_request = adapter.adapt_request(Platform.VOICE, original_request)

    print("Original request:", original_request)
    print("Web-adapted request:", web_request)
    print("Mobile-adapted request:", mobile_request)
    print("Voice-adapted request:", voice_request)

    # Example response adaptation
    original_response = {
        'message': 'I have added [BUTTON_DELETE] "buy groceries" to your todo list.',
        'status': 'success',
        'task_id': 123
    }

    web_response = adapter.adapt_response(Platform.WEB, original_response)
    mobile_response = adapter.adapt_response(Platform.MOBILE, original_response)
    voice_response = adapter.adapt_response(Platform.VOICE, original_response)

    print("\nOriginal response:", original_response)
    print("Web-adapted response:", web_response)
    print("Mobile-adapted response:", mobile_response)
    print("Voice-adapted response:", voice_response)

    # Check platform capabilities
    print(f"\nWeb platform supports graphics: {adapter.validate_platform_compatibility(Platform.WEB, 'graphics')}")
    print(f"Voice platform supports graphics: {adapter.validate_platform_compatibility(Platform.VOICE, 'graphics')}")
    print(f"Voice platform supports audio: {adapter.validate_platform_compatibility(Platform.VOICE, 'audio')}")