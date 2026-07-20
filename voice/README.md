# Voice Module - Text-to-Speech Generation

پوشه `voice` حاوی تمام کلاس‌ها و utility های مربوط به تولید صوت (TTS) است.

## معماری

### Design Patterns استفاده شده:

1. **Abstract Base Class**: کلاس `TTSProvider` یک interface مشترک برای تمام providers فراهم می‌کند
2. **Factory Pattern**: کلاس `TTSFactory` برای ایجاد instances از providers مختلف
3. **Strategy Pattern**: هر provider یک strategy متفاوت برای TTS فراهم می‌کند
4. **Manager Pattern**: کلاس `VoiceManager` برای مدیریت مرکزی

## فایل‌ها

### `base.py`
کلاس abstract برای تمام TTS providers:
- `TTSProvider`: base class
- `TTSConfig`: تنظیمات صوتی

### `edge_tts_provider.py`
پیاده‌سازی Microsoft Edge TTS:
- رایگان (نیازمند API Key نیست)
- فارسی support
- voice های: دیلارا، فرید

**نصب:**
```bash
pip install edge-tts
```

### `elevenlabs_provider.py`
پیاده‌سازی ElevenLabs API:
- کیفیت صوتی بالا
- بسیاری از languages و voices
- نیازمند API Key

**نصب:**
```bash
pip install requests
```

**API Key:**
دریافت از: https://elevenlabs.io

### `gemini_provider.py`
پیاده‌سازی Google Gemini API:
- Neural voices
- فارسی support
- نیازمند Google API Key

**نصب:**
```bash
pip install requests
```

**API Key:**
دریافت از: https://cloud.google.com/console

### `factory.py`
Factory برای ایجاد providers:
- `TTSFactory`: برای ایجاد instances
- `TTSProviderType`: enum انواع providers

### `config.py`
تنظیمات سیستم صوتی:
- `VoiceConfig`: dataclass برای تمام تنظیمات

### `manager.py`
مدیر مرکزی برای تمام عملیات صوتی:
- `VoiceManager`: رابط اصلی برای استفاده

### `utils.py`
Utility functions:
- `VoiceUtils`: توابع کمکی برای کار با صوت

### `examples.py`
مثال‌های استفاده

## استفاده

### مثال ساده (Edge TTS - رایگان)

```python
from voice import VoiceManager, VoiceConfig, TTSProviderType

# ایجاد config
config = VoiceConfig(
    provider_type=TTSProviderType.EDGE_TTS,
    speech_rate=1.0,
    pitch=1.0,
)

# ایجاد manager
manager = VoiceManager(config)

# تبدیل متن به صوت
audio_data = manager.synthesize_text(
    "سلام، این یک متن نمونه است.",
    speaker_type="moderator"
)

# ذخیره فایل
manager.save_audio(audio_data, "output.mp3")
```

### استفاده از ElevenLabs

```python
from voice import VoiceManager, VoiceConfig, TTSProviderType

config = VoiceConfig(
    provider_type=TTSProviderType.ELEVENLABS,
    elevenlabs_api_key="your_api_key_here",
)

manager = VoiceManager(config)
audio_data = manager.synthesize_text("متن شما")
```

### تبدیل بین Providers

```python
manager = VoiceManager()

# تبدیل به ElevenLabs
manager.switch_provider(
    TTSProviderType.ELEVENLABS,
    api_key="your_api_key_here"
)

# اکنون از ElevenLabs استفاده می‌شود
audio_data = manager.synthesize_text("متن جدید")
```

### به‌روز‌رسانی تنظیمات صوتی

```python
manager.update_voice_config(
    speech_rate=1.2,
    pitch=1.1,
    debater1_voice="fa-IR-Neural2-A",
)
```

### تقسیم متن طولانی

```python
from voice import VoiceUtils

long_text = "متن بسیار طولانی..."
chunks = VoiceUtils.split_long_text(long_text, max_length=5000)

for chunk in chunks:
    audio_data = manager.synthesize_text(chunk)
```

## Available Voices

### Edge TTS (فارسی)
- `fa-IR-DilaraNeural` - دیلارا (زن)
- `fa-IR-FaridNeural` - فرید (مرد)

### ElevenLabs
- `21m00Tcm4TlvDq8ikWAM` - Rachel
- `EXAVITQu4vr4xnSDxMaL` - Domi
- و بسیاری دیگر...

### Google Gemini (فارسی)
- `fa-IR-Standard-A`, `fa-IR-Standard-B`, `fa-IR-Standard-C`
- `fa-IR-Neural2-A`, `fa-IR-Neural2-B`, `fa-IR-Neural2-C`, `fa-IR-Neural2-D`

## معالجه خطا

```python
try:
    manager = VoiceManager(config)
    audio_data = manager.synthesize_text("متن")
except ValueError as e:
    print(f"خطای validation: {e}")
except RuntimeError as e:
    print(f"خطای runtime: {e}")
```

## اضافه کردن Provider جدید

```python
from voice import TTSProvider, TTSConfig, TTSFactory, TTSProviderType

class CustomTTSProvider(TTSProvider):
    def synthesize(self, text: str, speaker: str = "default") -> bytes:
        # پیاده‌سازی شما
        pass
    
    def get_available_voices(self) -> dict:
        return {}
    
    def validate_credentials(self) -> bool:
        return True

# ثبت provider
TTSFactory.register_provider(
    TTSProviderType.CUSTOM,
    CustomTTSProvider
)
```

## Performance Tips

1. **Caching**: نتایج صوتی را cache کنید تا از درخواست‌های مکرر جلوگیری شود
2. **Batch Processing**: متن‌های طولانی را به قطعات تقسیم کنید
3. **Provider Selection**: Edge TTS برای سرعت (رایگان)، ElevenLabs برای کیفیت بالا
4. **Error Handling**: همیشه exceptions را handle کنید

## مربوط به Dependencies

- `edge-tts`: برای Edge TTS
- `requests`: برای API calls (ElevenLabs, Gemini)
- PyQt5: برای UI integration

## Security

- API Keys را نکنید commit کنید
- از environment variables استفاده کنید
- هرگز API Keys را در logs log نکنید
