from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re
from termcolor import colored


def pc(text: str, color: str = "green") -> None:
    print(colored(text, color))


def slugify(s) -> str:
    s = s.lower().replace(" ", "-")
    s = re.sub(r'[^a-zA-Z0-9_-]', '', s).replace("--", "-")[:100]
    return s


def remove_query_parameters(url, parameters):
    url_parts = urlparse(url)
    query_params = parse_qs(url_parts.query)

    for param in parameters:
        query_params.pop(param, None)

    new_query_string = urlencode(query_params, doseq=True)

    new_url_parts = url_parts._replace(query=new_query_string)
    new_url = urlunparse(new_url_parts)

    return new_url
