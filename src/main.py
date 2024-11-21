import asyncio
from src.config.logger import logger_manager, logging
from src.libs.amazon.scraper import scrape_amazon


@logger_manager(name="main", log_level=logging.INFO, max_bytes=2_000_000)
async def main(log=None):
    await scrape_amazon("lattafa")


if __name__ == "__main__":
    asyncio.run(main())
