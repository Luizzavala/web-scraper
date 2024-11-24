import asyncio
from app.config import (logger_manager, logging, main_menu)
from app.common import amazon_scrapper, mercadolibre_scrapper, scrapper_map


@logger_manager(name="main", log_level=logging.INFO, max_bytes=2_000_000)
async def main(log=None):
    answers = await main_menu()
    selected_scrapper = scrapper_map.get(answers["ecommerce"])
    if selected_scrapper:
        await selected_scrapper(answers["product_name"])
    else:
        log.error(f"No scrapper found for {answers['ecommerce']}")


if __name__ == "__main__":
    asyncio.run(main())
