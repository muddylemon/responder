import re
import logging
from termcolor import colored

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pc(text: str, color: str = "green") -> None:
    print(colored(text, color))


def slugify(s) -> str:
    s = s.lower().replace(" ", "-")
    s = re.sub(r'[^a-zA-Z0-9_-]', '', s).replace("--", "-")[:100]
    return s
