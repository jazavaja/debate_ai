# settings/settings_manager.py
import json
import os
from pathlib import Path
from typing import Optional
from .settings_config import SettingsConfig, LLMProviderConfig


class SettingsManager:
    """مدیریت تنظیمات JSON"""
    
    DEFAULT_SETTINGS_DIR = Path.home() / ".debate_ai"
    DEFAULT_SETTINGS_FILE = DEFAULT_SETTINGS_DIR / "settings.json"
    
    @staticmethod
    def ensure_settings_dir() -> Path:
        """اطمینان از وجود دایرکتوری تنظیمات"""
        SettingsManager.DEFAULT_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        return SettingsManager.DEFAULT_SETTINGS_DIR
    
    @staticmethod
    def save_settings(settings: SettingsConfig, filepath: Optional[Path] = None) -> None:
        """ذخیره تنظیمات در فایل JSON"""
        if filepath is None:
            filepath = SettingsManager.DEFAULT_SETTINGS_FILE
        
        SettingsManager.ensure_settings_dir()
        
        data = settings.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_settings(filepath: Optional[Path] = None) -> SettingsConfig:
        """بارگذاری تنظیمات از فایل JSON"""
        if filepath is None:
            filepath = SettingsManager.DEFAULT_SETTINGS_FILE
        
        if not filepath.exists():
            return SettingsConfig()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SettingsConfig.from_dict(data)
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات: {e}")
            return SettingsConfig()
    
    @staticmethod
    def create_default_settings() -> SettingsConfig:
        """ایجاد تنظیمات پیش‌فرض"""
        settings = SettingsConfig(
            llm_providers=[
                LLMProviderConfig(
                    name="OpenAI (Default)",
                    provider="openai",
                    model="gpt-4o-mini",
                    api_key="",
                    base_uri="https://api.openai.com/v1",
                    priority=1,
                    enabled=True,
                ),
                LLMProviderConfig(
                    name="Anthropic",
                    provider="anthropic",
                    model="claude-3-5-sonnet-20241022",
                    api_key="",
                    base_uri="https://api.anthropic.com",
                    priority=2,
                    enabled=False,
                ),
                LLMProviderConfig(
                    name="Google Gemini",
                    provider="gemini",
                    model="gemini-1.5-flash",
                    api_key="",
                    base_uri="https://generativelanguage.googleapis.com/v1beta",
                    priority=3,
                    enabled=False,
                ),
            ],
            max_retries=3,
        )
        return settings
    
    @staticmethod
    def get_settings_path(custom_name: str = "") -> Path:
        """دریافت مسیر فایل تنظیمات"""
        SettingsManager.ensure_settings_dir()
        if custom_name:
            return SettingsManager.DEFAULT_SETTINGS_DIR / f"{custom_name}.json"
        return SettingsManager.DEFAULT_SETTINGS_FILE
    
    @staticmethod
    def list_saved_settings() -> list[str]:
        """دریافت لیست تنظیمات ذخیره شده"""
        SettingsManager.ensure_settings_dir()
        settings_files = list(SettingsManager.DEFAULT_SETTINGS_DIR.glob("*.json"))
        return [f.stem for f in settings_files]
