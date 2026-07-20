# voice/examples.py
"""
مثال‌های استفاده از Voice Module
"""

from core.voice import (
    VoiceManager,
    VoiceConfig,
    TTSProviderType,
    VoiceUtils,
)


def example_edge_tts():
    """مثال: استفاده از Edge TTS (رایگان، نیازمند API Key نیست)"""
    print("=== Edge TTS Example ===")
    
    config = VoiceConfig(
        provider_type=TTSProviderType.EDGE_TTS,
        speech_rate=1.0,
        pitch=1.0,
    )
    
    manager = VoiceManager(config)
    
    try:
        text = "سلام، این یک متن نمونه برای تبدیل به صوت است."
        audio_data = manager.synthesize_text(text, speaker_type="moderator")
        
        filepath = f"{VoiceUtils.get_output_directory()}/example_edge_tts.mp3"
        manager.save_audio(audio_data, filepath)
        
        print(f"✓ فایل صوتی ذخیره شد: {filepath}")
        print(f"✓ اندازه فایل: {VoiceUtils.get_file_size_mb(filepath):.2f} MB")
    except Exception as e:
        print(f"✗ خطا: {e}")


def example_elevenlabs():
    """مثال: استفاده از ElevenLabs API"""
    print("\n=== ElevenLabs Example ===")
    
    # نیاز به ElevenLabs API Key
    api_key = "your_elevenlabs_api_key_here"
    
    config = VoiceConfig(
        provider_type=TTSProviderType.ELEVENLABS,
        elevenlabs_api_key=api_key,
        speech_rate=1.0,
    )
    
    try:
        manager = VoiceManager(config)
        
        # بررسی صحت credentials
        if manager.validate_credentials():
            print("✓ API Key معتبر است")
            
            # دریافت voice های موجود
            voices = manager.get_available_voices()
            print(f"✓ Voice های موجود: {len(voices)}")
        else:
            print("✗ API Key نامعتبر است")
    except Exception as e:
        print(f"✗ خطا: {e}")


def example_gemini():
    """مثال: استفاده از Google Gemini API"""
    print("\n=== Gemini API Example ===")
    
    # نیاز به Google API Key
    api_key = "your_google_api_key_here"
    
    config = VoiceConfig(
        provider_type=TTSProviderType.GEMINI,
        gemini_api_key=api_key,
        debater1_voice="fa-IR-Neural2-A",
        debater2_voice="fa-IR-Neural2-B",
    )
    
    try:
        manager = VoiceManager(config)
        
        if manager.validate_credentials():
            print("✓ API Key معتبر است")
            voices = manager.get_available_voices()
            print(f"✓ Voice های موجود: {voices}")
        else:
            print("✗ API Key نامعتبر است")
    except Exception as e:
        print(f"✗ خطا: {e}")


def example_provider_switching():
    """مثال: تبدیل بین providers"""
    print("\n=== Provider Switching Example ===")
    
    manager = VoiceManager()
    print(f"✓ Provider فعلی: {manager.config.provider_type.value}")
    
    # تبدیل به provider دیگر
    try:
        manager.switch_provider(TTSProviderType.EDGE_TTS)
        print(f"✓ Provider جدید: {manager.config.provider_type.value}")
    except Exception as e:
        print(f"✗ خطا در تبدیل provider: {e}")


def example_long_text_splitting():
    """مثال: تقسیم متن طولانی"""
    print("\n=== Long Text Splitting Example ===")
    
    long_text = "این یک متن بسیار طولانی است. " * 100
    
    chunks = VoiceUtils.split_long_text(long_text, max_length=1000)
    print(f"✓ متن به {len(chunks)} قطعه تقسیم شد")
    print(f"✓ طول هر قطعه: {[len(c) for c in chunks[:3]]}...")


def example_full_debate_generation():
    """مثال: تولید صوت برای کل مناظره"""
    print("\n=== Full Debate Generation Example ===")
    
    config = VoiceConfig(
        provider_type=TTSProviderType.EDGE_TTS,
        speech_rate=1.0,
        pitch=1.0,
    )
    
    manager = VoiceManager(config)
    
    # داده‌های نمونه مناظره
    debate_data = {
        "topic": "آینده هوش مصنوعی",
        "turns": [
            {
                "speaker": "احمد",
                "speaker_type": "debater1",
                "content": "هوش مصنوعی آینده را تغییر خواهد داد.",
            },
            {
                "speaker": "فاطمه",
                "speaker_type": "debater2",
                "content": "اما باید از مخاطرات آن نیز آگاه باشیم.",
            },
            {
                "speaker": "مجری",
                "speaker_type": "moderator",
                "content": "نقاط جالبی مطرح شد. بیایید بحث را ادامه دهیم.",
            },
        ]
    }
    
    output_dir = VoiceUtils.get_output_directory("debate_audio")
    
    try:
        for turn in debate_data["turns"]:
            filename = VoiceUtils.generate_audio_filename(
                debate_data["topic"],
                turn["speaker"],
            )
            filepath = f"{output_dir}/{filename}"
            
            audio_data = manager.synthesize_text(
                turn["content"],
                speaker_type=turn["speaker_type"],
            )
            manager.save_audio(audio_data, filepath)
            
            print(f"✓ {turn['speaker']}: {filepath}")
            
    except Exception as e:
        print(f"✗ خطا: {e}")


if __name__ == "__main__":
    print("Voice Module Examples\n")
    
    # اجرای مثال‌ها
    example_edge_tts()
    example_provider_switching()
    example_long_text_splitting()
    
    # مثال‌های نیازمند API Key (فقط برای reference)
    # example_elevenlabs()
    # example_gemini()
    # example_full_debate_generation()
