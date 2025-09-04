from bs4 import BeautifulSoup


def extract_tag_value(raw_html, tag):
    parsed_html = BeautifulSoup(raw_html, 'html.parser')
    try:
        tag_value = parsed_html.find(tag).string
    except AttributeError:
        tag_value = None
    return tag_value


def extract_tag_attribute_value(raw_html, tag, attribute, required_attributes={}):
    parsed_html = BeautifulSoup(raw_html, 'html.parser')
    try:
        attribute_value = parsed_html.find(tag, attrs={
            **required_attributes,
            attribute: True
        }).get(attribute)
    except AttributeError:
        attribute_value = None
    return attribute_value
