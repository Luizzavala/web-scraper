import asyncio
from app.config import (logger_manager, logging)
from app.common import amazon_scrapper


@logger_manager(name="main", log_level=logging.INFO, max_bytes=2_000_000)
async def main(log=None):
    await amazon_scrapper("rtx 4070")

if __name__ == "__main__":
    asyncio.run(main())
