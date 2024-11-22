class recipeItem:
    def __init__(self, title: str = None, url: str = None, price: float = None):
        self.title: str = title
        self.url: str = url
        self.price: float = price

    def toDict(self):
        return {"title": self.title, "url": self.url, "price": self.price}
