from google import genai
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Provider برای Gemini با SDK رسمی google-genai
    استفاده از Interactions API
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = genai.Client(
            api_key=self.api_key
        )

    def chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """
        درخواست معمولی Gemini
        """

        prompt = f"""
System Instruction:
{system_prompt}

User:
{user_prompt}
"""

        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt,
        )

        return (interaction.output_text or "").strip()


    def chat_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        on_chunk
    ):
        """
        Stream پاسخ Gemini
        """

        prompt = f"""
System Instruction:
{system_prompt}

User:
{user_prompt}
"""

        stream = self.client.interactions.create(
            model=self.model,
            input=prompt,
            stream=True,
        )

        for event in stream:
            text = getattr(event, "text", None)

            if text:
                on_chunk(text)