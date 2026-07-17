#!/usr/bin/env python
"""تست streaming بهینه‌سازی پرامپت"""

import sys
from PyQt5.QtCore import QCoreApplication
from core.llm_client import LLMClient
from core.prompt_optimizer import PromptOptimizer

def test_streaming_optimize():
    """تست streaming optimize"""
    
    # نیاز به QCoreApplication برای PyQt signals
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    
    client = LLMClient()
    optimizer = PromptOptimizer(client)
    
    test_prompt = "شما یک متخصص هوش مصنوعی هستید که در مناظره‌های فنی شرکت می‌کند."
    test_name = "دکتر علی"
    
    print("🧪 تست streaming بهینه‌سازی پرامپت شروع شد...")
    print(f"📝 Prompt: {test_prompt[:60]}...")
    print(f"👤 Name: {test_name}")
    print("-" * 60)
    
    chunks_received = []
    final_result = []
    errors = []
    test_complete = False
    
    def on_chunk(chunk: str):
        chunks_received.append(chunk)
        print(f"📦 [{len(chunks_received)}] Chunk دریافت: {repr(chunk[:40])}")
    
    def on_success(text: str):
        nonlocal test_complete
        final_result.append(text)
        test_complete = True
        print(f"\n✅ بهینه‌سازی موفق!")
        print(f"📊 نتیجه نهایی ({len(text)} کاراکتر):\n{text[:150]}...\n")
        app.quit()
    
    def on_error(error: str):
        nonlocal test_complete
        errors.append(error)
        test_complete = True
        print(f"\n❌ خطا: {error}\n")
        app.quit()
    
    # فراخوانی optimize
    thread = optimizer.optimize(
        original_prompt=test_prompt,
        purpose="debater",
        name=test_name,
        on_chunk=on_chunk,
        on_success=on_success,
        on_error=on_error,
        use_stream=True
    )
    
    # اجرای app تا اتمام
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        test_streaming_optimize()
    except Exception as e:
        print(f"❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
