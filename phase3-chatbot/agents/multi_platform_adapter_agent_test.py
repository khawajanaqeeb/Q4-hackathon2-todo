"""
Tests for the Multi-Platform Adapter Agent
"""

import pytest
from agents.multi_platform_adapter_agent import (
    MultiPlatformAdapterAgent,
    Platform,
    PlatformCapabilities
)


def test_get_platform_capabilities():
    """Test retrieving platform capabilities."""
    adapter = MultiPlatformAdapterAgent()

    # Test web platform capabilities
    web_caps = adapter.get_platform_capabilities(Platform.WEB)
    assert web_caps.supports_graphics is True
    assert web_caps.supports_audio is False
    assert web_caps.screen_width == 1920
    assert web_caps.supports_rich_text is True

    # Test voice platform capabilities
    voice_caps = adapter.get_platform_capabilities(Platform.VOICE)
    assert voice_caps.supports_graphics is False
    assert voice_caps.supports_audio is True
    assert voice_caps.screen_width is None


def test_adapt_request_web():
    """Test adapting request for web platform."""
    adapter = MultiPlatformAdapterAgent()

    original_request = {
        'user_id': 'user123',
        'message': 'Add a new task to buy groceries',
        'timestamp': '2023-12-20T10:30:00Z'
    }

    adapted_request = adapter.adapt_request(Platform.WEB, original_request)

    assert adapted_request['user_id'] == 'user123'
    assert 'platform_metadata' in adapted_request
    assert adapted_request['platform_metadata']['platform'] == 'web'


def test_adapt_request_mobile():
    """Test adapting request for mobile platform."""
    adapter = MultiPlatformAdapterAgent()

    original_request = {
        'user_id': 'user123',
        'message': 'Add a new task to buy groceries',
        'timestamp': '2023-12-20T10:30:00Z'
    }

    adapted_request = adapter.adapt_request(Platform.MOBILE, original_request)

    assert adapted_request['user_id'] == 'user123'
    assert 'platform_metadata' in adapted_request
    assert adapted_request['platform_metadata']['platform'] == 'mobile'


def test_adapt_request_voice():
    """Test adapting request for voice platform."""
    adapter = MultiPlatformAdapterAgent()

    original_request = {
        'user_id': 'user123',
        'message': 'Add a new task to buy groceries',
        'timestamp': '2023-12-20T10:30:00Z'
    }

    adapted_request = adapter.adapt_request(Platform.VOICE, original_request)

    assert adapted_request['user_id'] == 'user123'
    assert 'platform_metadata' in adapted_request
    assert adapted_request['platform_metadata']['platform'] == 'voice'


def test_adapt_request_truncation():
    """Test that long requests are truncated for platforms with shorter limits."""
    adapter = MultiPlatformAdapterAgent()

    long_message = 'A' * 1500  # Longer than any platform's limit
    original_request = {
        'user_id': 'user123',
        'message': long_message,
        'timestamp': '2023-12-20T10:30:00Z'
    }

    adapted_request = adapter.adapt_request(Platform.VOICE, original_request)  # Voice has shortest limit

    # Should be truncated to max length for voice platform
    assert len(adapted_request['message']) <= 200


def test_adapt_response_web():
    """Test adapting response for web platform."""
    adapter = MultiPlatformAdapterAgent()

    original_response = {
        'message': 'I have added [BUTTON_DELETE] "buy groceries" to your todo list.',
        'status': 'success',
        'task_id': 123
    }

    adapted_response = adapter.adapt_response(Platform.WEB, original_response)

    assert 'formatted_for' in adapted_response
    assert adapted_response['formatted_for'] == 'web'
    assert 'adaptation_timestamp' in adapted_response


def test_adapt_response_voice():
    """Test adapting response for voice platform."""
    adapter = MultiPlatformAdapterAgent()

    original_response = {
        'message': 'I have added [BUTTON_DELETE] "buy groceries" to your todo list.',
        'status': 'success',
        'task_id': 123
    }

    adapted_response = adapter.adapt_response(Platform.VOICE, original_response)

    # Graphics elements should be converted for voice
    assert 'formatted_for' in adapted_response
    assert adapted_response['formatted_for'] == 'voice'


def test_initialize_platform_interface():
    """Test initializing platform interface."""
    adapter = MultiPlatformAdapterAgent()

    web_interface = adapter.initialize_platform_interface(Platform.WEB)
    mobile_interface = adapter.initialize_platform_interface(Platform.MOBILE)
    voice_interface = adapter.initialize_platform_interface(Platform.VOICE)

    assert web_interface['platform'] == 'web'
    assert mobile_interface['platform'] == 'mobile'
    assert voice_interface['platform'] == 'voice'

    assert 'capabilities' in web_interface
    assert 'capabilities' in mobile_interface
    assert 'capabilities' in voice_interface


def test_synchronize_state():
    """Test synchronizing state across platforms."""
    adapter = MultiPlatformAdapterAgent()

    result = adapter.synchronize_state(Platform.WEB, 'user123')

    assert result['user_id'] == 'user123'
    assert result['platform'] == 'web'
    assert result['sync_status'] == 'success'
    assert 'last_synced' in result
    assert 'synchronized_data' in result


def test_handle_platform_event_screen_resize():
    """Test handling platform-specific screen resize event."""
    adapter = MultiPlatformAdapterAgent()

    event = {
        'type': 'screen_resize',
        'data': {
            'dimensions': {
                'width': 1024,
                'height': 768
            }
        }
    }

    result = adapter.handle_platform_event(Platform.WEB, event)

    assert result['event_type'] == 'screen_resize'
    assert result['platform'] == 'web'
    assert result['action'] == 'adjust_layout'
    assert result['status'] == 'processed'


def test_handle_platform_event_voice_input():
    """Test handling platform-specific voice input event."""
    adapter = MultiPlatformAdapterAgent()

    event = {
        'type': 'voice_input',
        'data': {
            'transcript': 'Add a new task to buy groceries'
        }
    }

    result = adapter.handle_platform_event(Platform.VOICE, event)

    assert result['event_type'] == 'voice_input'
    assert result['platform'] == 'voice'
    assert result['action'] == 'process_speech'
    assert result['transcript'] == 'Add a new task to buy groceries'


def test_handle_platform_event_touch_gesture():
    """Test handling platform-specific touch gesture event."""
    adapter = MultiPlatformAdapterAgent()

    event = {
        'type': 'touch_gesture',
        'data': {
            'gesture': 'swipe_left'
        }
    }

    result = adapter.handle_platform_event(Platform.MOBILE, event)

    assert result['event_type'] == 'touch_gesture'
    assert result['platform'] == 'mobile'
    assert result['action'] == 'interpret_gesture'
    assert result['gesture'] == 'swipe_left'


def test_validate_platform_compatibility_graphics():
    """Test validating platform compatibility for graphics."""
    adapter = MultiPlatformAdapterAgent()

    # Web should support graphics
    assert adapter.validate_platform_compatibility(Platform.WEB, 'graphics') is True

    # Voice should not support graphics
    assert adapter.validate_platform_compatibility(Platform.VOICE, 'graphics') is False


def test_validate_platform_compatibility_audio():
    """Test validating platform compatibility for audio."""
    adapter = MultiPlatformAdapterAgent()

    # Voice should support audio
    assert adapter.validate_platform_compatibility(Platform.VOICE, 'audio') is True

    # Web should NOT support audio (according to our config)
    assert adapter.validate_platform_compatibility(Platform.WEB, 'audio') is False


def test_validate_platform_compatibility_rich_text():
    """Test validating platform compatibility for rich text."""
    adapter = MultiPlatformAdapterAgent()

    # Web should support rich text
    assert adapter.validate_platform_compatibility(Platform.WEB, 'rich_text') is True

    # Voice should NOT support rich text (according to our config)
    assert adapter.validate_platform_compatibility(Platform.VOICE, 'rich_text') is False


def test_get_available_platforms():
    """Test getting list of available platforms."""
    adapter = MultiPlatformAdapterAgent()

    platforms = adapter.get_available_platforms()

    assert Platform.WEB in platforms
    assert Platform.MOBILE in platforms
    assert Platform.VOICE in platforms
    assert Platform.DESKTOP in platforms
    assert Platform.MESSAGING in platforms
    assert Platform.SMART_DEVICE in platforms


def test_convert_graphics_to_text():
    """Test converting graphics to text."""
    adapter = MultiPlatformAdapterAgent()

    content = 'Click [BUTTON_ADD] to add [PROGRESS_BAR] status.'
    converted = adapter._convert_graphics_to_text(content)

    assert '(Button: Add)' in converted
    assert '[Progress: XXXXXXXXXX]' in converted


def test_strip_rich_text_formatting():
    """Test stripping rich text formatting."""
    adapter = MultiPlatformAdapterAgent()

    content = 'This is **bold** and *italic* text with a [link](http://example.com).'
    stripped = adapter._strip_rich_text_formatting(content)

    assert 'bold' in stripped
    assert 'italic' in stripped
    assert 'link' in stripped
    assert '**' not in stripped  # Bold markers removed
    assert '*' not in stripped   # Italic markers removed


def test_convert_to_speech_friendly_text():
    """Test converting text to speech-friendly format."""
    adapter = MultiPlatformAdapterAgent()

    content = 'I have a todo list with btn msg.'
    converted = adapter._convert_to_speech_friendly_text(content)

    assert 'to do' in converted  # 'todo' converted
    assert 'button' in converted  # 'btn' converted
    assert 'message' in converted  # 'msg' converted


def test_get_platform_specific_formatting_list():
    """Test getting platform-specific formatting for lists."""
    adapter = MultiPlatformAdapterAgent()

    content = [{'content': 'Buy groceries'}, {'content': 'Walk the dog'}]

    # For voice platform, lists should be converted to numbered verbal format
    formatted = adapter.get_platform_specific_formatting(Platform.VOICE, 'list', content)

    assert '1. Buy groceries' in str(formatted)
    assert '2. Walk the dog' in str(formatted)


def test_get_platform_specific_formatting_other():
    """Test getting platform-specific formatting for non-list content."""
    adapter = MultiPlatformAdapterAgent()

    content = "Just a regular string"

    # For non-list content, should return unchanged
    formatted = adapter.get_platform_specific_formatting(Platform.VOICE, 'list', content)

    assert formatted == content


def test_convert_graphics_to_simple_text():
    """Test converting graphics to simple text for messaging."""
    adapter = MultiPlatformAdapterAgent()

    content = 'Click [BUTTON_ADD] and [BUTTON_DELETE].'
    converted = adapter._convert_graphics_to_simple_text(content)

    assert 'ADD' in converted
    assert 'DELETE' in converted


def test_convert_graphics_to_basic_text():
    """Test converting graphics to basic text for smart devices."""
    adapter = MultiPlatformAdapterAgent()

    content = 'Click [BUTTON_ADD] and [BUTTON_DELETE].'
    converted = adapter._convert_graphics_to_basic_text(content)

    assert '+' in converted
    assert '-' in converted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])