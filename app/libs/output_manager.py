# stdlib
import os
from datetime import datetime
from typing import List, Optional

# external
import json
from aiofiles import open as aio_open
from bs4 import BeautifulSoup

async def save_results(
        content: Optional[str] = None,
        objects_list: Optional[List[object]] = None,
        soup: Optional[BeautifulSoup] = None,
        sku: str = "result",
) -> None:
    """
    Saves the results as HTML, soup (prettified), or JSON files in the 'outputs' folder.

    Args:
        content (Optional[str]): The raw HTML content to save.
        soup (Optional[BeautifulSoup]): The BeautifulSoup object to save as prettified HTML.
        objects_list (Optional[List[object]]): A list of objects to save as JSON.
        sku (str): The SKU or identifier for the files.

    Returns:
        object:
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
        print(f"HTML saved at: {html_path}")

    if objects_list:
        json_dir = os.path.join("outputs", "json")
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, f"scrapper-{sku}-{timestamp}.json")
        async with aio_open(json_path, "w") as f:
            serialized_data = json.dumps(
                [obj.__dict__ for obj in objects_list], indent=4
            )
            await f.write(serialized_data)
            print(f"JSON saved at: {json_path}")


    if soup:
        prettified_dir = os.path.join("outputs", "prettified")
        os.makedirs(prettified_dir, exist_ok=True)
        prettified_path = os.path.join(prettified_dir, f"scrapper-{sku}-{timestamp}.html")
        async with aio_open(prettified_path, "w", encoding="utf-8") as f:
            await f.write(soup.prettify())
            print(f"Prettified HTML saved at: {prettified_path}")

