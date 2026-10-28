import threading
from bisect import insort


def _rank(product: dict) -> tuple[int, int]:
    return (-product["popularity"], product["id"])


class _Node:
    def __init__(self) -> None:
        self.children: dict[str, _Node] = {}
        self.products: list[dict] = []


class ProductTrie:
    """Case-insensitive name prefix index. Each node holds its matches, most popular first."""

    def __init__(self, products: list[dict] | None = None) -> None:
        self._root = _Node()
        self._lock = threading.Lock()
        for product in products or []:
            self.insert(product)

    def insert(self, product: dict) -> None:
        with self._lock:
            node = self._root
            for char in product["name"].lower():
                node = node.children.setdefault(char, _Node())
                insort(node.products, product, key=_rank)

    def search(self, prefix: str) -> list[dict]:
        """O(len(prefix)) walk to the prefix node, then a copy of its matches."""
        with self._lock:
            node = self._root
            for char in prefix.lower():
                node = node.children.get(char)
                if node is None:
                    return []
            return list(node.products)
