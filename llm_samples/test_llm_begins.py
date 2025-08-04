import logging
from os import getenv

import httpx
import lmstudio as lms
import pytest
from bs4 import BeautifulSoup

LM_STUDIO_URL = getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")

transport = httpx.AsyncHTTPTransport(retries=3)


async def load_page_content(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for style_tag in soup.find_all("style"):
        style_tag.decompose()

    main_article_content = soup.find(["main", "article", "div"], class_="content")

    if main_article_content is None:
        raise ValueError("Anchors not found on page")

    with open("tmp/test.ignore.html", "w") as f:
        text = main_article_content.prettify()
        f.write()

    return soup


def list_of_models():
    return lms.list_downloaded_models()


pytestmark = pytest.mark.asyncio


@pytest.fixture
def testurl():
    return getenv("TEST_PAGE", "https://en.wikipedia.org/wiki/Python_(programming_language)")


def test_loading_lmstudio():
    print(list_of_models())


async def test_load_page(testurl: str):
    page = await load_page_content(testurl)
