import re


def slugify(s) -> str:
    s = s.lower().replace(" ", "-")
    s = re.sub(r'[^a-zA-Z0-9_-]', '', s).replace("--", "-")[:100]
    return s
