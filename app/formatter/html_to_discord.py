
from html import unescape
import re

def html_to_discord(message: str):
    replacements = {
        r"<\s*(b|strong)\s*>": "**",
        r"<\s*/\s*(b|strong)\s*>": "**",
        r"<\s*(i|em)\s*>": "*",
        r"<\s*/\s*(i|em)\s*>": "*",
        r"<\s*u\s*>": "__",
        r"<\s*/\s*u\s*>": "__",
        r"<\s*(s|strike|del)\s*>": "~~",
        r"<\s*/\s*(s|strike|del)\s*>": "~~",
        r"<\s*code\s*>": "`",
        r"<\s*/\s*code\s*>": "`",
        r"<\s*br\s*/?\s*>": "\n",
    }
    for pattern, replacement in replacements.items():
        message = re.sub(
            pattern,
            replacement,
            message,
            flags=re.IGNORECASE,
        )
        
    message = re.sub(
        r"<\s*/?\s*p\s*>",
        "\n",
        message,
        flags=re.IGNORECASE,
    )
    
    message = re.sub(r"<[^>]+>", "", message)
    return unescape(message).strip()