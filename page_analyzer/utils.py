from contextlib import contextmanager
from typing import Iterator
from urllib.parse import urlparse

import psycopg2
from bs4 import BeautifulSoup
from psycopg2.extras import DictCursor
from validators.url import url as validate_url


@contextmanager
def dict_cursor(dsn: str) -> Iterator[DictCursor]:
    """Connect to a database, provide a DictCursor, close the connection."""
    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                yield cur
    finally:
        conn.close()
                

def is_valid_url(url: str) -> bool:
    """Check whether the URL is valid and fits in 255 symbol limit."""
    if validate_url(url) and len(url) <= 255:
        return True
    return False


def clean_url(url: str) -> str:
    """Get scheme and hostname from a URL without anything else."""
    url_parts = urlparse(url)
    return f"{url_parts.scheme}://{url_parts.hostname}"


def extract_tag_value(raw_html: str, tag: str) -> str | None:
    """Extract tag value from raw HTML string."""
    parsed_html = BeautifulSoup(raw_html, 'html.parser')
    try:
        tag_value = parsed_html.find(tag).string
    except AttributeError:
        tag_value = None
    return tag_value


def extract_tag_attribute_value(
        raw_html: str,
        tag: str,
        attribute: str,
        required_attributes: dict[str, str | bool] | None = None
) -> str | None:
    """Extract attribute value from a specific tag in raw HTML string.
    Optionally, provide attribute-value pairs to be present
    in the same tag. Examples of such pairs:
    {'attribute': 'value'}  # str-str for specific values
    {'attribute': True}     # str-bool for values that should exist
    """
    if required_attributes is None:
        required_attributes = {}
    parsed_html = BeautifulSoup(raw_html, 'html.parser')
    try:
        attribute_value = parsed_html.find(tag, attrs={
            **required_attributes,
            attribute: True
        }).get(attribute)
    except AttributeError:
        attribute_value = None
    return attribute_value
