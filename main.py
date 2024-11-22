import asyncio
from app.config import (logger_manager, logging, main_menu)
from app.common import amazon_scrapper


@logger_manager(name="main", log_level=logging.INFO, max_bytes=2_000_000)
async def main(log=None):
    answers = await main_menu()
    await amazon_scrapper(answers["product_name"])


if __name__ == "__main__":
    asyncio.run(main())
