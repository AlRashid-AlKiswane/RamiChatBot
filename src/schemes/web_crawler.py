from pydantic import BaseModel, HttpUrl

class CrawlRequest(BaseModel):
    start_url: HttpUrl
    max_pages: int = 10