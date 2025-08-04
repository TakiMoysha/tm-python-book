import logging
import pytest
import pytest_asyncio
import hypothesis

import asyncio

from crawl4ai import AsyncWebCrawler, BM25ContentFilter, DefaultMarkdownGenerator, PruningContentFilter
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig


pytestmark = pytest.mark.asyncio


# as strategy through hypothesis
@pytest.fixture
def crawler_run_default_config():
    return CrawlerRunConfig(
        word_count_threshold=10,
        exclude_external_links=True,
        remove_overlay_elements=True,
        process_iframes=True,
    )


# as strategy through hypothesis
@pytest.fixture()
def browser_default_config():
    return BrowserConfig(
        verbose=True,
    )


async def test_crawl(browser_default_config, crawler_run_default_config):
    async with AsyncWebCrawler(config=browser_default_config) as crawler:
        raw_content_page = await crawler.arun(
            "https://blog.oddbit.com/post/2018-03-12-using-docker-macvlan-networks/#host-access",
            crawler_run_default_config,
        )

    # prune filter -
    prune_filter = PruningContentFilter(
        threshold=0.5,
        threshold_type="fixed",
        min_word_threshold=10,
    )
    md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
    prune_crawler_run_config = CrawlerRunConfig(markdown_generator=md_generator)

    # BM25 filter -
    bm25_filter = BM25ContentFilter(
        user_query="health benefits fruit",
        bm25_threshold=1.2,
    )
    md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
    bm25_crawler_run_config = CrawlerRunConfig(markdown_generator=md_generator)
