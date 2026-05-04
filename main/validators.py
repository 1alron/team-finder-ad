from django.core.exceptions import ValidationError

from .constants import GITHUB_URL_PREFIX


def validate_github_url(url):
    if url and not url.startswith(GITHUB_URL_PREFIX):
        raise ValidationError(f"Ссылка должна вести на ресурс GitHub (начинается с {GITHUB_URL_PREFIX})")
    return url
