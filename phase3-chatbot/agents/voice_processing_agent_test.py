"""
Tests for the Voice Processing Agent
"""

import pytest
import asyncio
from agents.voice_processing_agent import (
    VoiceProcessingAgent,
    AudioProcessor,
    MockSTTProvider,
    MockTTSService
)


@pytest.mark.asyncio
async def test_speech_to_text():
    """Test speech-to-text conversion."""
    agent = VoiceProcessingAgent()

    # Create dummy audio data
    dummy_audio = b'\x00' * 2000  # Some dummy audio data

    # Test transcription
    result = await agent.speech_to_text(dummy_audio)

    # Should return some text (even if mocked)
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_text_to_speech():
    """Test text-to-speech conversion."""
    agent = VoiceProcessingAgent()

    text_input = "Hello, this is a test."

    # Test synthesis
    audio_output = await agent.text_to_speech(text_input)

    # Should return audio data as bytes
    assert isinstance(audio_output, bytes)
    assert len(audio_output) > 0


def test_detect_voice_activity():
    """Test voice activity detection."""
    agent = VoiceProcessingAgent()

    # Test with silence
    silence_audio = b'\x00' * 1000
    is_voice_silence = agent.detect_voice_activity(silence_audio)

    # Test with some data (simulating voice)
    voice_audio = b'\x40\x00\x40\x00' * 250  # Some non-zero data
    is_voice_data = agent.detect_voice_activity(voice_audio)

    # Silence should not trigger voice activity
    assert is_voice_silence is False

    # Some data should trigger voice activity
    assert is_voice_data is True


def test_enhance_audio_quality():
    """Test audio quality enhancement."""
    agent = VoiceProcessingAgent()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Enhance audio quality
    enhanced_audio = agent.enhance_audio_quality(dummy_audio)

    # Should return audio data as bytes
    assert isinstance(enhanced_audio, bytes)
    assert len(enhanced_audio) == len(dummy_audio)


def test_cancel_echo():
    """Test echo cancellation."""
    agent = VoiceProcessingAgent()

    # Create dummy audio data
    input_audio = b'\x40\x00\x40\x00' * 500
    playback_audio = b'\x20\x00\x20\x00' * 500

    # Cancel echo
    echo_cancelled = agent.cancel_echo(input_audio, playback_audio)

    # Should return audio data as bytes
    assert isinstance(echo_cancelled, bytes)
    assert len(echo_cancelled) == len(input_audio)


def test_adjust_volume_levels():
    """Test volume level adjustment."""
    agent = VoiceProcessingAgent()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Adjust volume levels
    adjusted_audio = agent.adjust_volume_levels(dummy_audio)

    # Should return audio data as bytes
    assert isinstance(adjusted_audio, bytes)
    assert len(adjusted_audio) == len(dummy_audio)


def test_compress_audio():
    """Test audio compression."""
    agent = VoiceProcessingAgent()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Compress audio
    compressed_audio = agent.compress_audio(dummy_audio)

    # Should return audio data as bytes
    assert isinstance(compressed_audio, bytes)
    assert len(compressed_audio) == len(dummy_audio)


@pytest.mark.asyncio
async def test_process_voice_command():
    """Test complete voice command processing."""
    agent = VoiceProcessingAgent()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Process voice command
    text_command, response_audio = await agent.process_voice_command(dummy_audio)

    # Should return both text and audio
    assert isinstance(text_command, str)
    assert isinstance(response_audio, bytes)


@pytest.mark.asyncio
async def test_custom_stt_tts_providers():
    """Test using custom STT and TTS providers."""
    # Create custom providers
    custom_stt = MockSTTProvider()
    custom_tts = MockTTSService()

    # Initialize agent with custom providers
    agent = VoiceProcessingAgent(stt_provider=custom_stt, tts_provider=custom_tts)

    # Test with dummy audio
    dummy_audio = b'\x40\x00\x40\x00' * 500
    text_result = await agent.speech_to_text(dummy_audio)

    assert isinstance(text_result, str)


def test_audio_processor_normalize_audio():
    """Test audio normalization."""
    processor = AudioProcessor()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Normalize audio
    normalized = processor.normalize_audio(dummy_audio)

    # Should return audio data as bytes
    assert isinstance(normalized, bytes)
    assert len(normalized) == len(dummy_audio)


def test_audio_processor_detect_voice_activity():
    """Test voice activity detection in audio processor."""
    processor = AudioProcessor()

    # Test with silence
    silence_audio = b'\x00' * 1000
    is_voice_silence = processor.detect_voice_activity(silence_audio)

    # Test with some data
    voice_audio = b'\x40\x00\x40\x00' * 250
    is_voice_data = processor.detect_voice_activity(voice_audio)

    # Silence should not trigger voice activity
    assert is_voice_silence is False

    # Some data should trigger voice activity
    assert is_voice_data is True


def test_audio_processor_enhance_audio_quality():
    """Test audio enhancement in audio processor."""
    processor = AudioProcessor()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Enhance audio
    enhanced = processor.enhance_audio_quality(dummy_audio)

    # Should return audio data as bytes
    assert isinstance(enhanced, bytes)
    assert len(enhanced) == len(dummy_audio)


def test_audio_processor_cancel_echo():
    """Test echo cancellation in audio processor."""
    processor = AudioProcessor()

    # Create dummy audio data
    input_audio = b'\x40\x00\x40\x00' * 500
    playback_audio = b'\x20\x00\x20\x00' * 500

    # Cancel echo
    echo_cancelled = processor.cancel_echo(input_audio, playback_audio)

    # Should return audio data as bytes
    assert isinstance(echo_cancelled, bytes)
    assert len(echo_cancelled) == len(input_audio)


def test_audio_processor_compress_audio():
    """Test audio compression in audio processor."""
    processor = AudioProcessor()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Compress audio
    compressed = processor.compress_audio(dummy_audio)

    # Should return audio data as bytes
    assert isinstance(compressed, bytes)
    assert len(compressed) == len(dummy_audio)


@pytest.mark.asyncio
async def test_mock_stt_provider():
    """Test the mock STT provider."""
    provider = MockSTTProvider()

    # Create dummy audio data
    dummy_audio = b'\x40\x00\x40\x00' * 500

    # Transcribe audio
    result = await provider.transcribe(dummy_audio)

    # Should return a string
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_mock_tts_service():
    """Test the mock TTS service."""
    provider = MockTTSService()

    text = "Hello, this is a test."

    # Synthesize text
    result = await provider.synthesize(text)

    # Should return audio data as bytes
    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_voice_processing_agent_init():
    """Test initializing the voice processing agent."""
    agent = VoiceProcessingAgent()

    # Check that it has the required attributes
    assert hasattr(agent, 'stt_provider')
    assert hasattr(agent, 'tts_provider')
    assert hasattr(agent, 'sample_rate')
    assert hasattr(agent, 'audio_processor')


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])