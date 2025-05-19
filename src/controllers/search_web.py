
import logging
import os
import sys
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_transformers import Html2TextTransformer

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from helpers import Settings, get_settings
    from logs import log_debug, log_error, log_info
except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


class WebsiteCrawler:
    def __init__(self, start_url: str, max_pages: int = 100):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = deque([start_url])
        self.queued = set([start_url])
        self.domain = urlparse(start_url).netloc
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebCrawler/1.0; +https://example.com/bot)"
        }
        self.app_settings: Settings = get_settings()
        self.doc_dir = self.app_settings.DOC_LOCATION_SAVE
        os.makedirs(self.doc_dir, exist_ok=True)

    def crawl(self):
        log_info(f"Starting crawl from {self.start_url}")

        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.popleft()

            if url in self.visited:
                continue

            try:
                log_debug(f"Visiting: {url}")
                response = requests.get(url, headers=self.headers, timeout=5)

                if response.status_code != 200:
                    log_error(f"Non-200 status at {url}: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                self.visited.add(url)

                for link_tag in soup.find_all("a", href=True):
                    href = link_tag.get("href")
                    if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
                        continue

                    full_url = urljoin(url, href)
                    parsed = urlparse(full_url)

                    if parsed.netloc != self.domain:
                        continue

                    norm_url = parsed.scheme + "://" + parsed.netloc + parsed.path
                    if norm_url not in self.visited and norm_url not in self.queued:
                        self.to_visit.append(norm_url)
                        self.queued.add(norm_url)

            except requests.RequestException as e:
                log_error(f"Error visiting {url}: {e}")
            except Exception as e:
                log_error(f"Unexpected error at {url}: {e}")

        log_info(f"Crawling finished. Visited {len(self.visited)} pages.")
        return list(self.visited)

    def save_to_text_files(self, all_pages: list[str]):
        import tempfile

        from langchain_community.document_loaders import PyPDFLoader

        text_chunks = []

        for i, url in enumerate(all_pages):
            try:
                if url.lower().endswith(".pdf"):
                    log_info(f"Downloading PDF: {url}")
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(response.content)
                            tmp_file_path = tmp_file.name

                        loader = PyPDFLoader(tmp_file_path)
                        docs = loader.load()
                        text = "\n".join(doc.page_content for doc in docs)
                        os.remove(tmp_file_path)
                    else:
                        log_error(f"Failed to download PDF {url}")
                        continue
                else:
                    loader = WebBaseLoader([url])
                    docs = loader.load()

                    transformer = Html2TextTransformer()
                    text_docs = transformer.transform_documents(docs)
                    text = text_docs[0].page_content if text_docs else ""

                section_header = f"\n--- Page {i + 1}: {url} ---\n"
                text_chunks.append(section_header + text)

            except Exception as e:
                log_error(f"Error processing {url}: {e}")

        # Write all collected text to a single output file
        url_name = self.start_url.replace("/", "_").strip()
        url_name = url_name.replace("https:", "").strip()
        output_file = os.path.join(self.doc_dir, f"{url_name}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(text_chunks))

        log_info(f"All content (HTML + PDF) saved to {output_file}")
        return output_file




if __name__ == "__main__":
    base_url = "https://www.gig.com.jo/home"
    crawler = WebsiteCrawler(start_url=base_url, max_pages=1)
    
    # Step 1: Crawl all internal links
    all_pages = crawler.crawl()
    crawler.save_to_text_files(all_pages)
    print(f"Found {len(all_pages)} internal pages.")
    print()
    # Step 2: Save the crawled content as text files
    crawler.save_to_text_files(all_pages)
