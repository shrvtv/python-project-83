from validators.url import url as validate_url
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def is_valid_url(url: str) -> bool:
    if validate_url(url) and len(url) <= 255:
        return True
    return False

def clean_url(url: str) -> str:
    url_parts = urlparse(url)
    return f"{url_parts.scheme}://{url_parts.hostname}"


def extract_tag_value(raw_html, tag):
    parsed_html = BeautifulSoup(raw_html, 'html.parser')
    try:
        tag_value = parsed_html.find(tag).string
    except AttributeError:
        tag_value = None
    return tag_value


def extract_tag_attribute_value(raw_html, tag, attribute, required_attributes=None):
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
