# voice/gemini_provider.py
"""
Google Gemini API Provider - استفاده از Google Gemini TTS
"""

import requests
from typing import Optional
from core.voice.base import TTSProvider, TTSConfig


class GeminiProvider(TTSProvider):
    """
    TTS Provider برای Google Gemini API
    نیازمند: Google API Key
    """

    API_BASE_URL = "https://texttospeech.googleapis.com/v1"
    
    VOICES = {
        "fa-IR-Standard-A": "فارسی - الف",
        "fa-IR-Standard-B": "فارسی - ب",
        "fa-IR-Standard-C": "فارسی - ج",
        "fa-IR-Neural2-A": "فارسی Neural2 - الف",
        "fa-IR-Neural2-B": "فارسی Neural2 - ب",
        "fa-IR-Neural2-C": "فارسی Neural2 - ج",
        "fa-IR-Neural2-D": "فارسی Neural2 - د",
    }

    def __init__(self, api_key: str, config: Optional[TTSConfig] = None):
        super().__init__(config)
        if not api_key or not api_key.strip():
            raise ValueError("Google API Key الزامی است")
        self.api_key = api_key

    def synthesize(self, text: str, speaker: str = "fa-IR-Neural2-A") -> bytes:
        """
        تبدیل متن به صوت با Google Gemini
        
        Args:
            text: متن برای تبدیل
            speaker: voice ID
            
        Returns:
            bytes: داده‌های صوتی MP3
        """
        if not text or not text.strip():
            raise ValueError("متن نمی‌تواند خالی باشد")

        url = f"{self.API_BASE_URL}/text:synthesize"
        params = {"key": self.api_key}
        
        # استخراج language code از voice ID
        language_code = speaker.split("-")[0] + "-" + speaker.split("-")[1]
        
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": language_code,
                "name": speaker,
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "pitch": (self.config.pitch - 1) * 20,  # -20 to +20
                "speakingRate": self.config.speed,
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            
            data = response.json()
            if "audioContent" not in data:
                raise RuntimeError("پاسخ Gemini فاقد audioContent است")
            
            # audioContent معمولاً base64 encoded است
            import base64
            return base64.b64decode(data["audioContent"])
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Google API Key نامعتبر است")
            elif response.status_code == 429:
                raise RuntimeError("محدودیت Rate Limit Google API فعال است")
            else:
                raise RuntimeError(f"خطا در Google Gemini API: {str(e)}")
        except requests.exceptions.Timeout:
            raise RuntimeError("Timeout در ارتباط با Google Gemini API")
        except Exception as e:
            raise RuntimeError(f"خطا در تولید صوت Gemini: {str(e)}")

    def get_available_voices(self) -> dict:
        """دریافت voice های موجود"""
        return self.VOICES.copy()

    def validate_credentials(self) -> bool:
        """بررسی اعتبار API Key"""
        try:
            # تست کردن یک درخواست ساده
            url = f"{self.API_BASE_URL}/text:synthesize"
            params = {"key": self.api_key}
            
            payload = {
                "input": {"text": "test"},
                "voice": {
                    "languageCode": "fa-IR",
                    "name": "fa-IR-Neural2-A",
                },
                "audioConfig": {"audioEncoding": "MP3"}
            }
            
            response = requests.post(
                url,
                json=payload,
                params=params,
                timeout=10,
            )
            return response.status_code == 200
        except Exception:
            return False
