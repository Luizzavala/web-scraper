import asyncio
from InquirerPy import prompt
from rich.console import Console
from rich.panel import Panel
from ..libs import (BANNER_MENU)
from typing import Dict, Any


async def main_menu() -> Dict[str, str]:
    """
    Displays a menu for the user to input a product name and select an ecommerce platform.

    Returns:
        Dict[str, str]: A dictionary containing the product name and selected ecommerce platform.
    """
    console = Console()
    console.print(Panel(BANNER_MENU, style="cyan"))

    questions: list[Dict[str, Any]] = [
        {
            "type": "input",
            "name": "product_name",
            "message": "Introduce el producto en búsqueda:",
        },
        {
            "type": "list",
            "name": "ecommerce",
            "message": "Selecciona la plataforma de comercio:",
            "choices": ["Amazon", "MercadoLibre"],
        },
    ]
    answers: Dict[str, str] = await asyncio.to_thread(prompt, questions)
    return {"product_name": format_string(answers["product_name"]), "ecommerce": answers["ecommerce"]}


def format_string(string: str) -> str:
    return string.replace(" ", "_").lower()

