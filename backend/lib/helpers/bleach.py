import bleach

import re
import bleach


def sanitize_html(html: str) -> str:
    """
    Sanitize HTML content by removing disallowed tags and attributes.
    Strips all inline styles and CSS.

    Args:
        html (str): The raw HTML string to sanitize.

    Returns:
        str: The sanitized HTML string.
    """
    # Remove the contents of the <style> tag
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)

    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'img', 'div', 'span', 'br'
    ]

    # Disallowed tags: 'audio', 'font'

    allowed_attributes = {
        '*': ['class', 'id', 'title'],  # Global attributes
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'audio': ['controls', 'src'],
        'font': ['color', 'size', 'face'],
    }
    allowed_protocols = list(bleach.sanitizer.ALLOWED_PROTOCOLS) + ['data']
    cleaner = bleach.Cleaner(
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=True,  # Remove disallowed tags completely
        strip_comments=True
    )
    return cleaner.clean(html)
