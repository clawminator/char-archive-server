import requests


def parse_query_backend(query) -> list:
    response = requests.post('http://localhost:3000/search', data={'query': query})
    response.raise_for_status()
    return response.json()
