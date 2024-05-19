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


initialized = False
crawling_state = CrawlingState()
