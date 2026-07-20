# voice/__init__.py
"""
Voice Module - Text-to-Speech Generation
"""

from voice.base import TTSProvider, TTSConfig
from voice.edge_tts_provider import EdgeTTSProvider
from voice.elevenlabs_provider import ElevenLabsProvider
from voice.gemini_provider import GeminiProvider
from voice.factory import TTSFactory, TTSProviderType
from voice.config import VoiceConfig
from voice.manager import VoiceManager
from voice.utils import VoiceUtils

__all__ = [
    "TTSProvider",
    "TTSConfig",
    "EdgeTTSProvider",
    "ElevenLabsProvider",
    "GeminiProvider",
    "TTSFactory",
    "TTSProviderType",
    "VoiceConfig",
    "VoiceManager",
    "VoiceUtils",
]
