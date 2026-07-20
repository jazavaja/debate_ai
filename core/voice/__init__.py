# voice/__init__.py
"""
Voice Module - Text-to-Speech Generation
"""

from core.voice.base import TTSProvider, TTSConfig
from core.voice.edge_tts_provider import EdgeTTSProvider
from core.voice.elevenlabs_provider import ElevenLabsProvider
from core.voice.gemini_provider import GeminiProvider
from core.voice.factory import TTSFactory, TTSProviderType
from core.voice.config import VoiceConfig
from core.voice.manager import VoiceManager
from core.voice.utils import VoiceUtils

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
