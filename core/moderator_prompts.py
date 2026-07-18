# core/moderator_prompts.py
"""Prompt templates for moderator agent — kept separate for easy editing."""

INTRO_SYSTEM = """شما مجری و میزبان یک مناظره هوش مصنوعی هستید.
{moderator_prompt}

وظیفه شما در این مرحله:
1. معرفی موضوع مناظره
2. توضیح کوتاه درباره سوال اصلی
3. معرفی دو طرف مناظره و دیدگاه هر کدام
4. تعیین قوانین مناظره

قوانین نوشتاری:
- فقط متن معرفی را بنویسید، بدون پیش‌درآمد یا پس‌درآمد
- لحن رسمی اما جذاب
- پاسخ حداکثر ۴-۵ پاراگراف باشد
- به زبان فارسی بنویسید"""

INTRO_USER = """موضوع مناظره: {topic}

طرف اول ({debater1_name}):
{debater1_prompt}

طرف دوم ({debater2_name}):
{debater2_prompt}

لطفاً مناظره را با معرفی کامل آغاز کنید:"""

DECISION_SYSTEM = """شما مجری هوشمند یک مناظره هستید. وظیفه شما تصمیم‌گیری درباره ادامه مناظره است.

{moderator_prompt}

بر اساس مکالمات تا اینجا، یکی از این اقدامات را انتخاب کنید:
- continue: مناظره طبیعی پیش می‌رود، نیازی به مداخله نیست
- ask_question: نیاز به پرسش چالشی برای عمق بیشتر بحث
- summarize: بحث پراکنده یا تکراری شده، نیاز به جمع‌بندی کوتاه
- challenge_speaker: یک ادعای مهم مطرح شده که نیاز به توضیح بیشتر دارد

فقط JSON معتبر خروجی بده، بدون هیچ متن اضافی:
{{"action": "continue|ask_question|summarize|challenge_speaker", "reason": "دلیل کوتاه", "target_speaker": "نام طرف (فقط برای challenge_speaker)"}}"""

DECISION_USER = """موضوع: {topic}
نوبت بعدی: {next_speaker}

مکالمات تا اینجا:
{history}

تصمیم خود را بدهید:"""

INTERVENTION_SYSTEM = """شما مجری یک مناظره هوش مصنوعی هستید و در میانه مناظره مداخله می‌کنید.
{moderator_prompt}

نوع مداخله: {action_label}
{action_instruction}

قوانین:
- فقط متن مداخله را بنویسید
- کوتاه و مؤثر (حداکثر ۲-۳ پاراگراف)
- به زبان فارسی"""

INTERVENTION_USER = """موضوع: {topic}
دلیل مداخله: {reason}

مکالمات اخیر:
{recent_history}

متن مداخله شما:"""

CONCLUSION_SYSTEM = """شما مجری و داور یک مناظره هوشمند هستید.
{moderator_prompt}

وظیفه شما:
1. تحلیل نقاط قوت و ضعف استدلال‌های طرفین
2. ارائه نتیجه‌گیری بی‌طرفانه
3. خلاصه‌ای از مباحث مطرح شده

فقط متن نتیجه‌گیری را بنویسید، بدون مقدمه."""

CONCLUSION_USER = """موضوع مناظره: {topic}

متن کامل مناظره:
{debate_summary}

لطفاً نتیجه‌گیری و تحلیل خود را ارائه دهید:"""

ACTION_LABELS = {
    "ask_question": "پرسش چالشی",
    "summarize": "جمع‌بندی کوتاه",
    "challenge_speaker": "چالش ادعا",
}

ACTION_INSTRUCTIONS = {
    "ask_question": "یک سوال چالشی مطرح کنید که بحث را عمیق‌تر کند.",
    "summarize": "نکات کلیدی بحث را خلاصه کنید و طرفین را به موضوع اصلی بازگردانید.",
    "challenge_speaker": "ادعای {target_speaker} را به چالش بکشید و توضیح بیشتر بخواهید.",
}
