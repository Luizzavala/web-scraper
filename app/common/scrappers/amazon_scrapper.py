# stdlib
import os
from datetime import datetime
from typing import List, Optional

# external
import json
from aiofiles import open as aio_open
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# local
from libs.constant import AMAZON_URL
from libs.agent_manager import user_agent
from common.models.recipe_item import recipeItem


async def amazon_scrapper(sku: str) -> dict:
    """
    Scrapes an Amazon product page for a given SKU.

    Args:
        sku (str): The product SKU to scrape.

    Returns:
        dict: A dictionary containing a boolean indicating success and a message.
    """
    headers = {
        'User-Agent': user_agent()
    }
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=500)
        try:
            page = await browser.new_page(extra_http_headers=headers)
            await page.goto(f"{AMAZON_URL}{sku}")
            await page.wait_for_load_state("load")

            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")

            articles = _extract_articles(soup)

            await save_results(content=content, objects_list=articles, sku=sku)
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            await browser.close()

@staticmethod
def _extract_articles(soup: BeautifulSoup) -> List[recipeItem]:
    """
    Extracts articles from the BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The parsed HTML content.

    Returns:
        List[amazonItem]: A list of extracted articles.
    """

    articles = []
    article_containers = soup.find_all(attrs={"data-component-type": "s-search-result"})

    for container in article_containers:
        title_recipe = container.find(attrs={"data-cy": "title-recipe"})
        title_span = title_recipe.find("span") if title_recipe else None
        title = title_span.text.strip() if title_span else "Título no disponible"

        if title == "SponsoredSponsored":
            continue

        link_tag = title_recipe.find("a") if title_recipe else None
        base_url = AMAZON_URL.split("/s?k=")[0]
        url = (
            f"{base_url}{link_tag.get('href')}"
            if link_tag and link_tag.get("href")
            else "URL no disponible"
        )

        price_recipe = container.find(attrs={"data-cy": "price-recipe"})
        price_tag = (
            price_recipe.find(attrs={"class": "a-offscreen"}) if price_recipe else None
        )
        price = price_tag.text.strip() if price_tag else "Precio no disponible"

        articles.append(recipeItem(title=title, url=url, price=price))

    return articles

@staticmethod
async def save_results(
        content: Optional[str] = None,
        objects_list: Optional[List[recipeItem]] = None,
        sku: str = "result",
) -> None:
    """
    Saves the results as HTML or JSON files in the 'results' folder.

    Args:
        content (Optional[str]): The HTML content to save.
        objects_list (Optional[List[amazonItem]]): A list of objects to save as JSON.
        sku (str): The SKU or identifier for the files.

    Returns:
        None
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs("outputs", exist_ok=True)

    if content:
        html_dir = os.path.join("outputs", "html")
        os.makedirs(html_dir, exist_ok=True)
        html_path = os.path.join(html_dir, f"scrapper-{sku}-{timestamp}.html")
        async with aio_open(html_path, "w") as f:
            await f.write(content)

    if objects_list:
        json_dir = os.path.join("outputs", "json")
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, f"scrapper-{sku}-{timestamp}.json")
        async with aio_open(json_path, "w") as f:
            serialized_data = json.dumps(
                [obj.__dict__ for obj in objects_list], indent=4
            )
            await f.write(serialized_data)
