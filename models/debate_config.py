# models/debate_config.py
from dataclasses import dataclass, field
from typing import List
from .debater import Debater


@dataclass
class DebateConfig:
    """تنظیمات مناظره"""
    topic: str = ""
    debater1: Debater = field(default_factory=lambda: Debater(name="طرف اول"))
    debater2: Debater = field(default_factory=lambda: Debater(name="طرف دوم"))
    moderator: Debater = field(default_factory=lambda: Debater(name="مجری", role="moderator"))
    max_turns: int = 5
    temperature: float = 0.8

    def validate(self) -> tuple[bool, str]:
        """اعتبارسنجی تنظیمات"""
        if not self.topic.strip():
            return False, "موضوع مناظره نمی‌تواند خالی باشد"
        if not self.debater1.name.strip() or not self.debater2.name.strip():
            return False, "نام طرفین مناظره باید مشخص باشد"
        if self.max_turns < 1 or self.max_turns > 200:
            return False, "تعداد مکالمات باید بین ۱ تا ۲۰۰ باشد"
        return True, ""