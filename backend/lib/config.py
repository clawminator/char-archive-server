from pathlib import Path

CARD_IMAGE_ROOT_DIR = Path('/mnt/share/archive/hashed-data/')
if not CARD_IMAGE_ROOT_DIR.exists():
    CARD_IMAGE_ROOT_DIR = Path('/srv/chub-archive/archive/hashed-data')
assert CARD_IMAGE_ROOT_DIR.exists()

GLOBAL_SEARCH_INDEX = 'char-archive-search'

ELASTIC_HOST = 'https://172.0.3.105:9200'
ELASTIC_API_KEY = 'czhid2FvOEJLYkYtSnN1bXdMR1U6NEstN2xoS0pRY0s0NWc2LWRIWVRfQQ=='

MAX_SEARCH_RESULTS = 20

# Cache most routes for this many seconds.
GLOBAL_CACHE_SECONDS = 1800

# Origins that are allowed to access
ALLOWED_EXTERNAL_CORS_ORIGINS = [
    'https://lite.koboldai.net',
]
