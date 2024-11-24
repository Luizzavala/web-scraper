# stdlib
from typing import List

# external
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# local
from ...libs import (MERCADOLIBRE_URL, user_agent, save_results)
from .amazon_scrapper import recipeItem, urljoin

async def mercadolibre_scrapper(sku: str) -> dict:
    """
    Scrapes a MercadoLibre product page for a given SKU.

    Args:
        sku (str): The product SKU to scrape.

    Returns:
        dict: A dictionary containing a boolean indicating success and a message.
    """
    headers = {
        'User-Agent': user_agent()
    }
    search_url = f"{MERCADOLIBRE_URL}{sku}"
    all_products = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
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
                next_page = soup.select_one("a.andes-pagination__link[title='Siguiente']")
                if next_page and "href" in next_page.attrs:
                    search_url = urljoin(MERCADOLIBRE_URL, next_page["href"])
                else:
                    search_url = None

            # Guardar los artículos encontrados
            await save_results(objects_list=all_products, sku=sku)
            return {"success": True, "message": "Articulos encontrados"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            await browser.close()


async def _extract_articles(soup: BeautifulSoup) -> List[object]:
    """
    Extracts articles from the BeautifulSoup object.
    Args:
        soup (BeautifulSoup): The parsed HTML content.
    Returns:
        List[recipeItem]: A list of extracted articles.
    """
    product_containers = soup.find_all('li', class_='ui-search-layout__item shops__layout-item')
    products = []

    for container in product_containers:
        try:
            # Extraer el título
            title_tag = container.select_one("h2 a")
            title = title_tag.text.strip() if title_tag else "Título no disponible"

            # Extraer la URL
            url = title_tag["href"] if title_tag and title_tag.get("href") else "URL no disponible"

            # Extraer el precio
            currency_symbol = container.select_one(".andes-money-amount__currency-symbol")
            fraction = container.select_one(".andes-money-amount__fraction")
            cents = container.select_one(".andes-money-amount__cents")

            currency = currency_symbol.text.strip() if currency_symbol else "$"
            price_fraction = fraction.text.strip().replace(",", "") if fraction else "0"
            price_cents = cents.text.strip() if cents else "00"

            # Formatear el precio completo
            complete_price = float(f"{price_fraction}.{price_cents}")

            # Agregar el producto a la lista
            product = recipeItem(title=title, url=url, price=complete_price)
            products.append(product)

        except Exception as e:
            print(f"Error procesando un artículo: {e}")
            continue
    print(f"Productos encontrados: {len(products)}")
    return products
