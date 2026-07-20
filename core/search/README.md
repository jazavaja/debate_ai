# سیستم جستجوی وب (Web Search System) - DebateAI

## نمای کلی

سیستم جستجوی متحرک و قابل‌توسعه برای پروژه DebateAI که از الگوهای طراحی **Strategy** و **Factory** استفاده می‌کند. این سیستم قابلیت سوئیچ بین سرویس‌دهندگان مختلف جستجو را فراهم می‌کند و فالبک خودکار را پشتیبانی می‌کند.

## معماری

```
core/search/
├── __init__.py              # Export کلاس‌های اصلی
├── base.py                  # کلاس‌های پایه و Dataclass
├── config.py                # تنظیمات و Enum‌ها
├── factory.py               # Factory Pattern برای ساخت Provider
├── manager.py               # SearchManager - رابط اصلی
└── providers/
    ├── __init__.py
    ├── duckduckgo_provider.py   # DuckDuckGo (رایگان، بدون API Key)
    ├── tavily_provider.py       # Tavily API
    ├── serper_provider.py       # Serper (Google Search)
    ├── bing_provider.py         # Azure Bing Search
    └── brave_provider.py        # Brave Search API
```

## ویژگی‌های کلیدی

### 1. الگوی Strategy
هر سرویس‌دهنده جستجو (`DuckDuckGoProvider`, `TavilyProvider` و غیره) یک استراتژی جستجوی مختلف را پیاده‌سازی می‌کند. تمام آن‌ها از `BaseSearchProvider` ارث‌بری می‌کنند.

### 2. الگوی Factory
کلاس `SearchFactory` مسئول ایجاد نمونه‌های صحیح سرویس‌دهنده است. سرویس‌دهندگان جدید می‌توانند آسانی ثبت شوند.

### 3. Fallback خودکار
اگر سرویس‌دهنده اولیه ناموفق باشد، سیستم به صورت خودکار به `DuckDuckGo` (بدون نیاز به API Key) سوئیچ می‌کند.

### 4. قالب‌بندی Markdown
نتایج به صورت Markdown قالب‌بندی‌شده برای تزریق به LLM تهیه می‌شوند.

## استفاده

### مثال ساده

```python
from core.search import SearchManager, SearchConfig, SearchProviderType

# ایجاد تنظیمات
config = SearchConfig(
    active_provider=SearchProviderType.DUCKDUCKGO,
    default_max_results=3,
    enable_fallback=True
)

# ایجاد مدیر
manager = SearchManager(config)

# جستجو
result = manager.search("artificial intelligence", max_results=5)
print(result)
```

### تغییر سرویس‌دهنده

```python
# جابجایی به Tavily
success = manager.set_provider(SearchProviderType.TAVILY)
if success:
    result = manager.search("quantum computing")
```

### دریافت اطلاعات

```python
# نام سرویس‌دهنده فعال
provider = manager.get_active_provider()  # "duckduckgo"

# فهرست تمام سرویس‌دهندگان موجود
providers = manager.get_available_providers()
# ['duckduckgo', 'tavily', 'serper', 'bing', 'brave']
```

## سرویس‌دهندگان

### DuckDuckGo (DuckDuckGoProvider)
- **رایگان**: بدون نیاز به API Key
- **بسته مورد نیاز**: `duckduckgo-search` یا `ddgs`
- **خصوصیات**: فالبک به `region="wt-wt"` در صورت عدم نتیجه
- **نصب**: `pip install ddgs`

### Tavily (TavilyProvider)
- **API Key مورد نیاز**: `TAVILY_API_KEY`
- **بسته مورد نیاز**: `tavily-python`
- **نصب**: `pip install tavily-python`

### Serper (SerperProvider)
- **API Key مورد نیاز**: `SERPER_API_KEY`
- **API Endpoint**: `https://google.serper.dev/search`
- **توضیح**: جستجوی Google از طریق Serper.dev

### Bing (BingProvider)
- **API Key مورد نیاز**: `BING_SEARCH_API_KEY`
- **API Endpoint**: Azure Bing Web Search API
- **توضیح**: سرویس جستجو Microsoft Azure

### Brave (BraveProvider)
- **API Key مورد نیاز**: `BRAVE_SEARCH_API_KEY`
- **API Endpoint**: `https://api.search.brave.com/res/v1/web/search`
- **توضیح**: موتور جستجوی حریم‌خصوصی Brave

## متغیرهای محیطی

```bash
# سرویس‌دهنده فعال (پیش‌فرض: duckduckgo)
SEARCH_PROVIDER=duckduckgo

# حداکثر تعداد نتایج (پیش‌فرض: 3)
SEARCH_MAX_RESULTS=3

# کلیدهای API
TAVILY_API_KEY=your_tavily_key
SERPER_API_KEY=your_serper_key
BING_SEARCH_API_KEY=your_bing_key
BRAVE_SEARCH_API_KEY=your_brave_key
```

## کلاس‌های اصلی

### SearchResult (Dataclass)
نمایندگی یک نتیجه جستجو:
```python
@dataclass
class SearchResult:
    title: str              # عنوان نتیجه
    body: str               # متن خلاصه
    url: str                # لینک
    source_provider: str    # نام سرویس‌دهنده
```

### BaseSearchProvider (Abstract Class)
کلاس پایه برای تمام سرویس‌دهندگان:
```python
class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        pass
```

### SearchConfig (Dataclass)
تنظیمات سیستم جستجو:
```python
@dataclass
class SearchConfig:
    active_provider: SearchProviderType = SearchProviderType.DUCKDUCKGO
    default_max_results: int = 3
    enable_fallback: bool = True
    fallback_provider: SearchProviderType = SearchProviderType.DUCKDUCKGO
    # ... API Keys
```

### SearchFactory
کارخانه ایجاد سرویس‌دهندگان:
```python
class SearchFactory:
    @classmethod
    def register(cls, provider_type: SearchProviderType, 
                 provider_class: Type[BaseSearchProvider]) -> None:
        # ثبت سرویس‌دهنده جدید
        
    @classmethod
    def create(cls, provider_type: SearchProviderType, 
               config: SearchConfig) -> BaseSearchProvider:
        # ایجاد نمونه سرویس‌دهنده
```

### SearchManager
رابط اصلی برای سیستم جستجو:
```python
class SearchManager:
    def search(self, query: str, max_results: Optional[int] = None) -> str:
        # جستجو با فالبک خودکار
        
    def set_provider(self, provider_type: SearchProviderType) -> bool:
        # تغییر سرویس‌دهنده
        
    def get_active_provider(self) -> str:
        # دریافت نام سرویس‌دهنده فعال
        
    def get_available_providers(self) -> list:
        # دریافت فهرست سرویس‌دهندگان موجود
```

## مدیریت خطا

تمام سرویس‌دهندگان دارای مدیریت خطای جامع هستند:
- خطاهای شبکه را می‌گیرند
- API errors را مدیریت می‌کنند
- لیست خالی یا پیام خطا را برمی‌گردانند (بدون crash)
- لاگ می‌کنند برای دیباگ

## logging

سیستم از `logging` استاندارد Python استفاده می‌کند:

```python
import logging

logging.basicConfig(level=logging.INFO)
# یا
logger = logging.getLogger("core.search")
```

## نکات اضافی

1. **نصب بسته‌های اختیاری**:
   ```bash
   pip install ddgs requests tavily-python
   ```

2. **DuckDuckGo بدون API Key**: بهترین گزینه برای شروع و fallback

3. **قابلیت توسعه**: سرویس‌دهندگان جدید را به راحتی می‌توانید اضافه کنید

4. **Type Hinting**: تمام کد از type hints استفاده می‌کند

5. **Docstrings**: تمام کلاس‌ها و متدها دارای توضیحات فارسی و انگلیسی هستند

## تست

فایل تست ساده:
```bash
python test_search_simple.py
```

## مثال‌های بیشتر

### جستجوی متعدد با fallback

```python
manager = SearchManager()

queries = [
    "artificial intelligence",
    "machine learning",
    "deep learning"
]

for query in queries:
    result = manager.search(query)
    print(f"Query: {query}")
    print(result)
    print("-" * 50)
```

### تغییر Provider بر اساس موارد مختلف

```python
config = SearchConfig(
    active_provider=SearchProviderType.SERPER,
    fallback_provider=SearchProviderType.DUCKDUCKGO,
    enable_fallback=True
)

manager = SearchManager(config)

# اگر SERPER ناموفق بود، خودکار به DuckDuckGo می‌رود
result = manager.search("debate strategies")
```

## لایسنس

بخشی از پروژه DebateAI
