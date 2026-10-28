from app.trie import ProductTrie


def product(id, name, popularity):
    return {"id": id, "name": name, "popularity": popularity}


HAMMER = product(1, "Hammer", 5)
HAND_SAW = product(2, "Hand Saw", 2)
DRILL = product(3, "Drill", 9)


def make_trie():
    return ProductTrie([HAND_SAW, HAMMER, DRILL])


def test_search_returns_prefix_matches_most_popular_first():
    assert make_trie().search("h") == [HAMMER, HAND_SAW]
    assert make_trie().search("ha") == [HAMMER, HAND_SAW]


def test_search_narrows_as_prefix_grows():
    trie = make_trie()

    assert trie.search("ham") == [HAMMER]
    assert trie.search("han") == [HAND_SAW]
    assert trie.search("hand saw") == [HAND_SAW]


def test_search_ignores_case():
    assert make_trie().search("HA") == [HAMMER, HAND_SAW]


def test_search_returns_empty_for_no_match_or_empty_prefix():
    trie = make_trie()

    assert trie.search("x") == []
    assert trie.search("hammers") == []
    assert trie.search("") == []


def test_equal_popularity_ties_break_by_id():
    hatchet = product(4, "Hatchet", 5)
    trie = ProductTrie([hatchet, HAMMER])

    assert trie.search("ha") == [HAMMER, hatchet]


def test_insert_adds_product_in_rank_order():
    trie = make_trie()
    hatchet = product(4, "Hatchet", 3)

    trie.insert(hatchet)

    assert trie.search("ha") == [HAMMER, hatchet, HAND_SAW]
