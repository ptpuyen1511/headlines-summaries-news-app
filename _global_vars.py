class CrawlingState:
    def __init__(self):
        self.is_crawling = False
        self.type_crawl = ''
        self.thread_id = -1

    def set(self, is_crawling: bool, type_crawl: str, thread_id: int):
        self.is_crawling = is_crawling
        self.type_crawl = type_crawl
        self.thread_id = thread_id

    def __str__(self):
        return f'is_crawling={self.is_crawling}, type_crawl={self.type_crawl}, thread_id={self.thread_id}'

class TrendingKWCache:
    def __init__(self):
        self.is_running = False
        self.data : 'list[tuple[str,str]]' = list()
    
    def set(self, data: 'list[tuple[str,str]]'):
        self.data = data

    def get(self) -> 'list[tuple[str,str]]':
        return self.data

initialized = False
crawling_state = CrawlingState()
trending_kw_cache = TrendingKWCache()
