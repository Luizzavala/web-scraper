import random
from libs.constant import BROWSER_AGENTS

def user_agent() -> str:
    """
    A property that returns a randomly selected User-Agent string
    from the constant list `BROWSER_AGENTS`.

    Returns:
        str: A randomly selected User-Agent string.
    """
    return str(random.choice(BROWSER_AGENTS))
