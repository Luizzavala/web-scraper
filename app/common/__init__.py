# Models
from .models import recipeItem

# Scrappers
from .scrappers import amazon_scrapper
from .scrappers import mercadolibre_scrapper

scrapper_map = {
    "Amazon": amazon_scrapper,
    "MercadoLibre": mercadolibre_scrapper
}

__all__ = ["recipeItem", "amazon_scrapper", "mercadolibre_scrapper", "scrapper_map"]
