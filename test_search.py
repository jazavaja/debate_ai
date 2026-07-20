from ddgs import DDGS


class SearchTool:
    @staticmethod
    def search(query: str, max_results: int = 3) -> str:
        results = []
        try:
            with DDGS() as ddgs:
                # اولویت ۱: سعی در دریافت نتایج کلی (بدون سخت‌گیری در region)
                search_results = list(ddgs.text(query, max_results=max_results))

                # اگر با متد اول نتیجه‌ای دریافت نشد، با پارامتر عمومی‌تر تست می‌شود
                if not search_results:
                    search_results = list(ddgs.text(keywords=query, region="wt-wt", max_results=max_results))

                if search_results:
                    for r in search_results:
                        title = r.get('title', 'بدون عنوان')
                        body = r.get('body', 'بدون متن')
                        href = r.get('href', '#')
                        results.append(f"- **{title}**: {body} (منبع: {href})")

        except Exception as e:
            return f"خطا در انجام جستجو: {str(e)}"

        return "\n\n".join(results) if results else "نتیجه‌ای یافت نشد."


if __name__ == "__main__":
    test_query = "آخرین اخبار هوش مصنوعی"
    print(f"🔎 در حال جستجو برای: '{test_query}'...\n")

    output = SearchTool.search(test_query, max_results=3)

    print("📄 خروجی دریافت شده:")
    print("-" * 40)
    print(output)
    print("-" * 40)