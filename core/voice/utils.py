# voice/utils.py
"""
Utility functions برای Voice/TTS
"""

import os
from datetime import datetime
from typing import List, Tuple


class VoiceUtils:
    """کلاسی برای utility functions صوتی"""

    @staticmethod
    def get_output_directory(base_dir: str = "voice_output") -> str:
        """
        دریافت یا ایجاد دایرکتوری خروجی صوت
        
        Args:
            base_dir: دایرکتوری پایه
            
        Returns:
            مسیر دایرکتوری
        """
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @staticmethod
    def generate_audio_filename(
        topic: str,
        speaker: str,
        extension: str = "mp3",
        timestamp: bool = True,
    ) -> str:
        """
        تولید نام فایل صوتی
        
        Args:
            topic: موضوع
            speaker: نام speaker
            extension: پسوند فایل
            timestamp: افزودن timestamp
            
        Returns:
            نام فایل
        """
        safe_topic = "".join(
            c for c in topic if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_speaker = "".join(
            c for c in speaker if c.isalnum() or c in ("-", "_")
        ).rstrip()

        if timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"audio_{safe_topic}_{safe_speaker}_{ts}.{extension}"
        else:
            return f"audio_{safe_topic}_{safe_speaker}.{extension}"

    @staticmethod
    def split_long_text(
        text: str,
        max_length: int = 5000,
    ) -> List[str]:
        """
        تقسیم متن طولانی به قطعات کوچک‌تر
        برخی TTS providers محدودیت length دارند
        
        Args:
            text: متن
            max_length: حداکثر طول قطعه
            
        Returns:
            لیست قطعات
        """
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""

        sentences = text.split(".")
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + "."

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def get_file_size_mb(filepath: str) -> float:
        """
        دریافت اندازه فایل به مگابایت
        
        Args:
            filepath: مسیر فایل
            
        Returns:
            اندازه به MB
        """
        if os.path.exists(filepath):
            return os.path.getsize(filepath) / (1024 * 1024)
        return 0.0

    @staticmethod
    def cleanup_old_files(
        directory: str,
        max_age_hours: int = 24,
    ) -> int:
        """
        حذف فایل‌های قدیمی‌تر از مدت زمان مشخص
        
        Args:
            directory: دایرکتوری
            max_age_hours: حداکثر سن فایل به ساعت
            
        Returns:
            تعداد فایل‌های حذف شده
        """
        import time

        if not os.path.exists(directory):
            return 0

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted_count = 0

        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except Exception:
                        pass

        return deleted_count

    @staticmethod
    def validate_audio_file(filepath: str) -> Tuple[bool, str]:
        """
        بررسی صحت فایل صوتی
        
        Args:
            filepath: مسیر فایل
            
        Returns:
            (valid: bool, message: str)
        """
        if not os.path.exists(filepath):
            return False, "فایل وجود ندارد"

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return False, "فایل خالی است"

        if file_size > 500 * 1024 * 1024:  # 500MB
            return False, "فایل بیش از حد بزرگ است (>500MB)"

        return True, "فایل معتبر است"
