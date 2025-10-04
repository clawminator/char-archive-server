from typing import Tuple, List, Dict

from lib.sources import Sources


class Handler:
    def __init__(self, source: Sources, parts: list, node_type: str, version: int):
        self.source = source
        self.node_type = node_type
        self.version = version
        try:
            self._parts = self._build_parts(parts.copy())
        except:
            self._parts = None

    @property
    def parts(self):
        return self._parts

    def _build_parts(self, parts: list) -> list:
        return parts

    def check_parts(self) -> Tuple[int, str | None]:
        raise NotImplementedError

    def handle_node(self) -> Tuple[dict | None, int, str | None]:
        raise NotImplementedError

    def handle_image(self) -> Tuple[bytes | None, int, str | None]:
        raise NotImplementedError

    def handle_def(self, original_unmodified: bool) -> Tuple[dict | None, int, str | None]:
        raise NotImplementedError

    def handle_ratings(self) -> Tuple[List[Dict] | None, int, str | None]:
        raise NotImplementedError

    def handle_chats(self) -> Tuple[List[Dict] | None, int, str | None]:
        raise NotImplementedError

    def handle_user(self, username: str) -> dict | None:
        raise NotImplementedError

    def get_hidden(self) -> dict:
        raise NotImplementedError
