# stdlib
from typing import List

# external
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urljoin

# local
from ...libs import (AMAZON_URL, user_agent, save_results)
from app.common import recipeItem


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
    search_url = f"{AMAZON_URL}{sku}"
    all_products = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=500)
        try:

            page = await browser.new_page(extra_http_headers=headers)

            while search_url:
                await page.goto(search_url)
                await page.wait_for_load_state("load")

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")

                # Extraer los artículos de la página actual
                products = await _extract_articles(soup)
                all_products.extend(products)

                # Buscar el enlace de la siguiente página
                next_page = soup.select_one("a.s-pagination-next")
                if next_page and "href" in next_page.attrs:
                    search_url = urljoin(AMAZON_URL, next_page["href"])
                else:
                    search_url = None

            await save_results(
                objects_list=all_products,
                sku=sku
            )

            return {"success": True, "message": "Articulos encontrados"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            await browser.close()


async def _extract_articles(soup: BeautifulSoup) -> List[recipeItem]:
    """
    Extracts articles from the BeautifulSoup object.
    Args:
        soup (BeautifulSoup): The parsed HTML content.
    Returns:
        List[amazonItem]: A list of extracted articles.
    """
    product_containers = soup.find_all("div", attrs={"data-component-type": "s-search-result"})
    products = []

    for container in product_containers:
        # Extraer el título
        title_tag = container.select_one("h2 a span")
        title = title_tag.text.strip() if title_tag else "Título no disponible"

        # Extraer la URL
        link_tag = container.select_one("h2 a")
        base_url = AMAZON_URL.split("/s?k=")[0]
        url = urljoin(base_url, link_tag["href"]) if link_tag and link_tag.get("href") else "URL no disponible"

        # Extraer el precio
        price_tag = container.select_one(".a-price .a-offscreen")
        price = price_tag.text.strip() if price_tag else "Precio no disponible"

        products.append(recipeItem(title=title, url=url, price=price))

    return products