# voice/elevenlabs_provider.py
"""
ElevenLabs API Provider - استفاده از ElevenLabs API
"""

import requests
from typing import Optional
from core.voice.base import TTSProvider, TTSConfig


class ElevenLabsProvider(TTSProvider):
    """
    TTS Provider برای ElevenLabs API
    نیازمند: ElevenLabs API Key
    """

    API_BASE_URL = "https://api.elevenlabs.io/v1"
    
    VOICES = {
        "21m00Tcm4TlvDq8ikWAM": "Rachel",
        "EXAVITQu4vr4xnSDxMaL": "Domi",
        "MF3mGyEYCHXYMXV5eZiA": "Ava",
        "TxGEqnHWrfWFTfGW9XjX": "Josh",
        "VR6AewLTigWG4xSOukaG": "Arnold",
        "pNInz6obpgDQGcFmaJgB": "Adam",
        "yoZ06aMxZJJ28mfd3POQ": "Sam",
    }

    def __init__(self, api_key: str, config: Optional[TTSConfig] = None):
        super().__init__(config)
        if not api_key or not api_key.strip():
            raise ValueError("ElevenLabs API Key الزامی است")
        self.api_key = api_key
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def synthesize(self, text: str, speaker: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
        """
        تبدیل متن به صوت با ElevenLabs
        
        Args:
            text: متن برای تبدیل
            speaker: voice ID
            
        Returns:
            bytes: داده‌های صوتی MP3
        """
        if not text or not text.strip():
            raise ValueError("متن نمی‌تواند خالی باشد")

        url = f"{self.API_BASE_URL}/text-to-speech/{speaker}"
        
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("ElevenLabs API Key نامعتبر است")
            elif response.status_code == 429:
                raise RuntimeError("محدودیت Rate Limit ElevenLabs فعال است")
            else:
                raise RuntimeError(f"خطا در ElevenLabs API: {str(e)}")
        except requests.exceptions.Timeout:
            raise RuntimeError("Timeout در ارتباط با ElevenLabs API")
        except Exception as e:
            raise RuntimeError(f"خطا در تولید صوت ElevenLabs: {str(e)}")

    def get_available_voices(self) -> dict:
        """دریافت voice های موجود"""
        return self.VOICES.copy()

    def validate_credentials(self) -> bool:
        """بررسی اعتبار API Key"""
        try:
            url = f"{self.API_BASE_URL}/user"
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
