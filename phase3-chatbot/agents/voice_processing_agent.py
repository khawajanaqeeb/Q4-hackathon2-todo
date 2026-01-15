"""
Voice Processing Agent

Handles speech-to-text and text-to-speech conversion for voice-enabled interactions with the Todo AI Chatbot.
"""

import asyncio
import io
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import wave
import numpy as np
from datetime import datetime


class AudioProcessor:
    """Handles low-level audio processing operations."""

    @staticmethod
    def normalize_audio(audio_data: bytes, target_level: float = 0.8) -> bytes:
        """Normalize audio level to prevent clipping."""
        # Convert bytes to numpy array for processing
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Calculate current level and scaling factor
        current_max = np.max(np.abs(audio_array))
        if current_max == 0:
            return audio_data

        scale_factor = (target_level * 32767) / current_max

        # Apply normalization
        normalized_array = (audio_array * scale_factor).astype(np.int16)
        return normalized_array.tobytes()

    @staticmethod
    def detect_voice_activity(audio_data: bytes, threshold: float = 0.01) -> bool:
        """Detect if voice activity is present in the audio."""
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

        # Calculate RMS energy
        rms_energy = np.sqrt(np.mean(audio_array ** 2))

        # Return True if energy exceeds threshold
        return bool(rms_energy > threshold)

    @staticmethod
    def enhance_audio_quality(audio_data: bytes) -> bytes:
        """Apply basic audio enhancements."""
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Apply basic noise reduction (simple smoothing)
        enhanced_array = np.convolve(audio_array, np.ones(3)/3, mode='same')

        # Convert back to bytes
        return enhanced_array.astype(np.int16).tobytes()

    @staticmethod
    def cancel_echo(audio_input: bytes, playback_audio: bytes) -> bytes:
        """Basic echo cancellation."""
        # Convert to numpy arrays
        input_array = np.frombuffer(audio_input, dtype=np.int16).astype(np.float32)
        playback_array = np.frombuffer(playback_audio, dtype=np.int16).astype(np.float32)

        # Simple adaptive filtering for echo cancellation
        # In a real implementation, this would be more sophisticated
        if len(playback_array) > 0:
            # Align lengths
            min_len = min(len(input_array), len(playback_array))
            input_array = input_array[:min_len]
            playback_array = playback_array[:min_len]

            # Subtract echo (with some damping factor)
            echo_cancelled = input_array - 0.7 * playback_array
            echo_cancelled = np.clip(echo_cancelled, -32768, 32767)
            return echo_cancelled.astype(np.int16).tobytes()

        return audio_input

    @staticmethod
    def compress_audio(audio_input: bytes) -> bytes:
        """Compress audio for efficient transmission."""
        # Apply basic compression (reduce bit depth simulation)
        audio_array = np.frombuffer(audio_input, dtype=np.int16)

        # Apply compression by reducing amplitude variation
        compressed = np.clip(audio_array * 0.8, -32768, 32767)
        return compressed.astype(np.int16).tobytes()


class SpeechToTextProvider(ABC):
    """Abstract base class for STT providers."""

    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        pass


class TextToSpeechProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        pass


class MockSTTProvider(SpeechToTextProvider):
    """Mock STT provider for testing purposes."""

    async def transcribe(self, audio_data: bytes) -> str:
        """Mock transcription - returns predefined text based on audio size."""
        # In a real implementation, this would call an actual STT service
        # For now, return a mock response based on the audio characteristics
        if len(audio_data) > 1000:  # If there's substantial audio data
            # Simulate different responses based on the audio data
            if b'\x00' in audio_data[:50]:  # Check for silence at start
                return "add a new task to buy groceries"
            else:
                return "show me my todos"
        else:
            return ""


class MockTTSService(TextToSpeechProvider):
    """Mock TTS provider for testing purposes."""

    async def synthesize(self, text: str) -> bytes:
        """Mock synthesis - returns dummy audio data."""
        # In a real implementation, this would call an actual TTS service
        # For now, return dummy audio data
        # Create a simple wave format with some dummy data
        duration = len(text) * 0.1  # Approximate duration based on text length
        sample_rate = 22050
        frames = int(duration * sample_rate)

        # Generate simple sine wave pattern for demo
        t = np.linspace(0, duration, frames, False)
        freq = 440  # A4 note
        audio_wave = np.sin(2 * np.pi * freq * t)

        # Convert to 16-bit PCM
        audio_wave = (audio_wave * 32767).astype(np.int16)

        return audio_wave.tobytes()


class VoiceProcessingAgent:
    """
    Handles speech-to-text and text-to-speech conversion for voice-enabled interactions.
    """

    def __init__(self, stt_provider: Optional[SpeechToTextProvider] = None,
                 tts_provider: Optional[TextToSpeechProvider] = None,
                 sample_rate: int = 22050, language_code: str = 'en-US'):
        self.stt_provider = stt_provider or MockSTTProvider()
        self.tts_provider = tts_provider or MockTTSService()
        self.sample_rate = sample_rate
        self.language_code = language_code
        self.audio_processor = AudioProcessor()

    async def speech_to_text(self, audio_input: bytes) -> str:
        """
        Convert speech to text for user commands.
        """
        try:
            # Preprocess audio
            processed_audio = self.audio_processor.enhance_audio_quality(audio_input)
            processed_audio = self.audio_processor.normalize_audio(processed_audio)

            # Perform transcription
            text = await self.stt_provider.transcribe(processed_audio)
            return text
        except Exception as e:
            raise RuntimeError(f"Speech-to-text conversion failed: {str(e)}")

    async def text_to_speech(self, text_input: str) -> bytes:
        """
        Convert text to speech for responses.
        """
        try:
            # Generate speech from text
            audio_data = await self.tts_provider.synthesize(text_input)

            # Post-process audio
            processed_audio = self.audio_processor.normalize_audio(audio_data)
            return processed_audio
        except Exception as e:
            raise RuntimeError(f"Text-to-speech conversion failed: {str(e)}")

    def detect_voice_activity(self, audio_stream: bytes) -> bool:
        """
        Identify speech in audio stream.
        """
        return self.audio_processor.detect_voice_activity(audio_stream)

    def enhance_audio_quality(self, audio_input: bytes) -> bytes:
        """
        Improve audio quality for better processing.
        """
        return self.audio_processor.enhance_audio_quality(audio_input)

    def cancel_echo(self, audio_input: bytes, playback_audio: bytes) -> bytes:
        """
        Remove echo from input audio.
        """
        return self.audio_processor.cancel_echo(audio_input, playback_audio)

    def adjust_volume_levels(self, audio_input: bytes) -> bytes:
        """
        Normalize audio levels.
        """
        return self.audio_processor.normalize_audio(audio_input)

    def compress_audio(self, audio_input: bytes) -> bytes:
        """
        Compress for transmission.
        """
        return self.audio_processor.compress_audio(audio_input)

    async def process_voice_command(self, audio_input: bytes) -> Tuple[str, bytes]:
        """
        Process a complete voice command: convert speech to text, then return both
        the transcribed text and an audio response.
        """
        # Convert speech to text
        text_command = await self.speech_to_text(audio_input)

        # Generate response text (in a real implementation, this would be from the chatbot)
        if text_command.strip():
            response_text = f"You said: {text_command}. I received your voice command."
        else:
            response_text = "I couldn't understand your voice command. Could you please repeat?"

        # Convert response text to speech
        response_audio = await self.text_to_speech(response_text)

        return text_command, response_audio


# Example usage
if __name__ == "__main__":
    import asyncio

    # Initialize the voice processing agent
    voice_agent = VoiceProcessingAgent()

    # Example audio input (dummy data for testing)
    dummy_audio = b'\x00' * 44100  # 1 second of silence at 44.1kHz

    async def example():
        print("Processing voice command...")

        # Process voice command
        text_command, response_audio = await voice_agent.process_voice_command(dummy_audio)

        print(f"Recognized command: {text_command}")
        print(f"Response audio length: {len(response_audio)} bytes")

        # Test individual functions
        print("\nTesting individual functions:")

        # Test voice activity detection
        is_voice = voice_agent.detect_voice_activity(dummy_audio)
        print(f"Voice activity detected: {is_voice}")

        # Test audio enhancement
        enhanced_audio = voice_agent.enhance_audio_quality(dummy_audio)
        print(f"Enhanced audio length: {len(enhanced_audio)} bytes")

        # Test text-to-speech
        response = await voice_agent.text_to_speech("Hello, this is a test response.")
        print(f"TTS audio length: {len(response)} bytes")

    # Run the example
    asyncio.run(example())