import os
import sys
import tracemalloc
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

# Setup import path and logging
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from controllers import WebsiteCrawler
    from schemes import CrawlRequest

except ImportError as e:
    raise ImportError(f"[IMPORT ERROR] {__file__}: {e}")

crawler_route = APIRouter()


@crawler_route.post("/crawl")
async def crawl_website(request: CrawlRequest):
    tracemalloc.start()
    try:
        log_info(f"Received crawl request for {request.start_url}")
        crawler = WebsiteCrawler(start_url=str(request.start_url), max_pages=request.max_pages)

        visited = crawler.crawl()
        if not visited:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No pages were visited during crawl"
            )

        saved_file = crawler.save_to_text_files(visited)

        current, peak = tracemalloc.get_traced_memory()
        log_info(f"Memory usage during crawl: Current = {current / 1024:.2f} KB, Peak = {peak / 1024:.2f} KB")
        tracemalloc.stop()

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "file_path": saved_file
            }
        )

    except HTTPException as http_err:
        log_error(f"HTTP error: {http_err.detail}")
        raise http_err

    except Exception as e:
        tb = traceback.format_exc()
        log_error(f"Internal Server Error during crawl:\n{tb}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error occurred during crawling"
        )
