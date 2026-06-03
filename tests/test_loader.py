from src.ingestion.loader import clean_text


def test_newlines_replaced():
    assert clean_text("a\nb") == "a b"


def test_hyphenation_removed():
    assert clean_text("hyphen-\nated") == "hyphenated"


def test_camelcase_split():
    assert clean_text("camelCase") == "camel Case"


def test_page_marker_removed():
    assert "Page 5" not in clean_text("Page 5 text")


def test_whitespace_collapsed():
    assert clean_text("a   b") == "a b"


def test_empty_string():
    assert clean_text("") == ""
