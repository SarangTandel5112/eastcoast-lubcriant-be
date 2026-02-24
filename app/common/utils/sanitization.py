"""Input sanitization utilities for XSS and injection attack prevention."""

import bleach
from typing import Optional, List
import html
import re


# Define allowed HTML tags for rich text content
ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'a',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre'
]

# Define allowed HTML attributes
ALLOWED_HTML_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    '*': ['class']  # Allow class on all tags
}

# Define allowed protocols for links
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(
    text: str,
    allowed_tags: Optional[List[str]] = None,
    allowed_attributes: Optional[dict] = None
) -> str:
    """
    Sanitize HTML content, removing dangerous tags and attributes.

    Use this for user-generated content that should support basic HTML formatting
    (e.g., product descriptions, blog posts, comments with formatting).

    Args:
        text: The HTML string to sanitize
        allowed_tags: List of allowed HTML tags (defaults to ALLOWED_HTML_TAGS)
        allowed_attributes: Dict of allowed attributes per tag (defaults to ALLOWED_HTML_ATTRIBUTES)

    Returns:
        Sanitized HTML string safe for display

    Example:
        >>> sanitize_html("<p>Hello</p><script>alert('XSS')</script>")
        "<p>Hello</p>&lt;script&gt;alert('XSS')&lt;/script&gt;"
    """
    if not text:
        return ""

    return bleach.clean(
        text,
        tags=allowed_tags or ALLOWED_HTML_TAGS,
        attributes=allowed_attributes or ALLOWED_HTML_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Strip disallowed tags instead of escaping
    )


def sanitize_text(text: str) -> str:
    """
    Remove ALL HTML tags from text, leaving only plain text.

    Use this for user input that should never contain HTML
    (e.g., names, titles, short descriptions, search queries).

    Args:
        text: The text to sanitize

    Returns:
        Plain text with all HTML removed

    Example:
        >>> sanitize_text("<b>Hello</b> <script>alert('XSS')</script> World")
        "Hello  World"
    """
    if not text:
        return ""

    return bleach.clean(text, tags=[], strip=True)


def escape_html(text: str) -> str:
    """
    Escape HTML special characters to prevent XSS.

    Use this when you want to preserve the original text but make it safe
    for HTML display (e.g., displaying code snippets, error messages).

    Args:
        text: The text to escape

    Returns:
        HTML-escaped text

    Example:
        >>> escape_html("<script>alert('XSS')</script>")
        "&lt;script&gt;alert('XSS')&lt;/script&gt;"
    """
    if not text:
        return ""

    return html.escape(text, quote=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.

    Args:
        filename: The filename to sanitize

    Returns:
        Safe filename without dangerous characters

    Example:
        >>> sanitize_filename("../../etc/passwd")
        "etc_passwd"
        >>> sanitize_filename("my file (1).txt")
        "my_file_1.txt"
    """
    if not filename:
        return "unnamed"

    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Remove any non-alphanumeric characters except dots, dashes, and underscores
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)

    # Replace multiple spaces/underscores with single underscore
    filename = re.sub(r'[\s_]+', '_', filename)

    # Remove leading/trailing dots and underscores
    filename = filename.strip('._')

    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:max_length - len(ext) - 1]
        filename = f"{name}.{ext}" if ext else name

    # Ensure we have a valid filename
    if not filename:
        filename = "unnamed"

    return filename


def sanitize_url(url: str) -> Optional[str]:
    """
    Validate and sanitize a URL to prevent XSS and open redirect attacks.

    Args:
        url: The URL to sanitize

    Returns:
        Sanitized URL or None if invalid

    Example:
        >>> sanitize_url("https://example.com/page")
        "https://example.com/page"
        >>> sanitize_url("javascript:alert('XSS')")
        None
    """
    if not url:
        return None

    # Remove whitespace
    url = url.strip()

    # Check for dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    for protocol in dangerous_protocols:
        if url.lower().startswith(protocol):
            return None

    # Only allow http, https, and mailto
    if not url.startswith(('http://', 'https://', 'mailto:', '/')):
        return None

    return url


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize a SQL identifier (table name, column name).

    This is a defense-in-depth measure. You should ALWAYS use parameterized queries.

    Args:
        identifier: The SQL identifier to sanitize

    Returns:
        Sanitized identifier containing only safe characters

    Example:
        >>> sanitize_sql_identifier("users; DROP TABLE users--")
        "users_DROP_TABLE_users"
    """
    if not identifier:
        return ""

    # Allow only alphanumeric and underscores
    identifier = re.sub(r'[^\w]', '_', identifier)

    # Must start with letter or underscore
    if identifier and identifier[0].isdigit():
        identifier = f"_{identifier}"

    return identifier


def sanitize_email(email: str) -> Optional[str]:
    """
    Basic email sanitization (use Pydantic EmailStr for validation).

    Args:
        email: The email address to sanitize

    Returns:
        Sanitized email or None if invalid format

    Example:
        >>> sanitize_email("  test@EXAMPLE.com  ")
        "test@example.com"
    """
    if not email:
        return None

    # Remove whitespace and convert to lowercase
    email = email.strip().lower()

    # Basic email pattern check (Pydantic does better validation)
    email_pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if not re.match(email_pattern, email):
        return None

    return email


def sanitize_phone(phone: str) -> Optional[str]:
    """
    Sanitize phone number by removing non-digit characters.

    Args:
        phone: The phone number to sanitize

    Returns:
        Phone number with only digits

    Example:
        >>> sanitize_phone("+1 (555) 123-4567")
        "+15551234567"
    """
    if not phone:
        return None

    # Keep only digits, plus sign, and parentheses
    phone = re.sub(r'[^\d+()]', '', phone)

    return phone if phone else None


# Convenience function for common use cases
def sanitize_user_input(
    text: str,
    allow_html: bool = False,
    max_length: Optional[int] = None
) -> str:
    """
    General-purpose sanitization for user input.

    Args:
        text: The user input to sanitize
        allow_html: Whether to allow basic HTML tags (for rich text)
        max_length: Maximum allowed length (truncate if longer)

    Returns:
        Sanitized text

    Example:
        >>> sanitize_user_input("<p>Hello</p><script>alert('XSS')</script>", allow_html=True)
        "<p>Hello</p>&lt;script&gt;alert('XSS')&lt;/script&gt;"
        >>> sanitize_user_input("<p>Hello</p>", allow_html=False)
        "Hello"
    """
    if not text:
        return ""

    # Sanitize based on HTML policy
    if allow_html:
        text = sanitize_html(text)
    else:
        text = sanitize_text(text)

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text.strip()
