# utils/file_handler.py
import os
from datetime import datetime
from typing import List
from core.debate_engine import DebateTurn


class FileHandler:
    """
    هندلر ذخیره خروجی مناظره
    فرمت Markdown برای TTS-friendly بودن
    """

    @staticmethod
    def export_debate(topic: str,
                      debater1_name: str, debater1_prompt: str,
                      debater2_name: str, debater2_prompt: str,
                      moderator_name: str, moderator_prompt: str,
                      turns: List[DebateTurn],
                      conclusion: str,
                      output_dir: str = "debates") -> str:
        """
        ذخیره مناظره به فرمت Markdown

        Returns:
            مسیر فایل ذخیره شده
        """
        # ساخت پوشه اگه وجود نداره
        os.makedirs(output_dir, exist_ok=True)

        # نام فایل با timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"debate_{safe_topic}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        # ساخت محتوای Markdown
        content = FileHandler._build_markdown(
            topic, debater1_name, debater1_prompt,
            debater2_name, debater2_prompt,
            moderator_name, moderator_prompt,
            turns, conclusion
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    @staticmethod
    def _build_markdown(topic: str,
                        debater1_name: str, debater1_prompt: str,
                        debater2_name: str, debater2_prompt: str,
                        moderator_name: str, moderator_prompt: str,
                        turns: List[DebateTurn],
                        conclusion: str) -> str:
        """ساخت محتوای Markdown بهینه برای TTS"""

        lines = [
            f"# مناظره: {topic}",
            "",
            f"**تاریخ:** {datetime.now().strftime('%Y/%m/%d %H:%M')}",
            f"**تعداد نوبت‌ها:** {len(turns)}",
            "",
            "---",
            "",
            "## معرفی مجری",
            "",
            f"**{moderator_name}**",
            "",
            f"{moderator_prompt}",
            "",
            "---",
            "",
            "## معرفی طرفین مناظره",
            "",
            f"### {debater1_name}",
            "",
            f"{debater1_prompt}",
            "",
            f"### {debater2_name}",
            "",
            f"{debater2_prompt}",
            "",
            "---",
            "",
            "## متن کامل مناظره",
            "",
        ]

        # اضافه کردن مکالمات
        for turn in turns:
            lines.append(f"### نوبت {turn.turn_number}: {turn.speaker}")
            lines.append("")
            lines.append(turn.content)
            lines.append("")
            lines.append("---")
            lines.append("")

        # نتیجه‌گیری
        lines.extend([
            "",
            "## نتیجه‌گیری و تحلیل مجری",
            "",
            f"**{moderator_name}:**",
            "",
            conclusion,
            "",
            "---",
            "",
            "## راهنمای تبدیل به صوت (TTS)",
            "",
            "برای تبدیل این متن به صوت با Google Text-to-Speech:",
            "",
            "1. متن بالا را کپی کنید",
            "2. به Google Cloud TTS Console بروید",
            "3. از Voice Type `WaveNet` یا `Neural2` استفاده کنید",
            "4. برای هر شخصیت، Voice متفاوت انتخاب کنید:",
            f"   - {debater1_name}: Voice A (مثلاً `fa-IR-Wavenet-D`)",
            f"   - {debater2_name}: Voice B (مثلاً `fa-IR-Wavenet-B`)",
            f"   - {moderator_name}: Voice C (مثلاً `fa-IR-Wavenet-A`)",
            "",
            "> **نکته:** علامت‌های `---` نشان‌دهنده پause بین بخش‌ها هستند.",
            "",
            "---",
            "",
            "*تولید شده توسط DebateAI*",
        ])

        return "\n".join(lines)