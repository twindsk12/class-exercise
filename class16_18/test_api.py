import sqlite3

import pytest
from fastapi.testclient import TestClient

import main
from check_storage import BookStorage

#The `storage` fixture gives each test a separate temporary database
@pytest.fixture
def storage(tmp_path):
    return BookStorage(tmp_path / "books.db")

#The `client` fixture shows how to connect temporary storage to API tests
@pytest.fixture
def client(storage, monkeypatch):
    monkeypatch.setattr(main, "storage", storage)
    monkeypatch.setattr(main, "cache", main.BookCache())
    with TestClient(main.app) as test_client:
        yield test_client

def test_storage_persists(storage):
    book_id = storage.add_book("Book A", 12.5)
    reopened = BookStorage(storage.db_path)
    book = reopened.get_book(book_id)
    assert book["title"] == "Book A"
    assert book["price"] == 12.5

def test_failed_replacement_rolls_back(storage):
    storage.add_book("Book A", 12.5)
    storage.add_book("Book B", 25.0)

    before = storage.list_books()

    with pytest.raises(sqlite3.IntegrityError):
        storage.replace_books([
            ("New Book", 20.0),
            (None, 10.0)
        ])

    reopened = BookStorage(storage.db_path)

    assert reopened.list_books() == before

def test_cache_hit_skips_database(client, monkeypatch):
    response = client.post("/books", json={"title": "Book A", "price": 12.5})
    assert response.status_code == 200

    first = client.get("/books", params={"min_price": 0, "limit": 100})
    assert first.status_code == 200

    def fail_if_called(*args, **kwargs):
        pytest.fail("A cache hit should not query the database")

    monkeypatch.setattr(main.storage, "list_books", fail_if_called)

    second = client.get("/books", params={"min_price": 0, "limit": 100})
    assert second.status_code == 200
    assert second.json() == first.json()

def test_add_book_invalidates_cache(client):
    # TODO 1: Send two GET requests with min_price=0:
    # one with limit=1 and another with limit=100.
    # Assert 200 and check both entries using main.cache.get(0, limit).
    # TODO 2: repeat limit=100 and check the same response.
    # TODO 3: POST Book B at 20.0; assert 200 and both old entries are None.
    # TODO 4: GET again with limit=100; check both books,
    # their price-descending order, and the cached response.
    response = client.post(
        "/books",
        json={"title": "Book A", "price": 12.5}
    )
    assert response.status_code == 200

    client.get("/books", params={"min_price": 0, "limit": 1})
    client.get("/books", params={"min_price": 0, "limit": 100})

    # Confirm both results are cached
    assert main.cache.get(0, 1) is not None
    assert main.cache.get(0, 100) is not None

    response = client.post(
        "/books",
        json={"title": "Book B", "price": 20.0}
    )
    assert response.status_code == 200

    assert main.cache.get(0, 1) is None
    assert main.cache.get(0, 100) is None

    updated = client.get(
        "/books",
        params={"min_price": 0, "limit": 100}
    )

    assert updated.status_code == 200
    books = updated.json()

    assert len(books) == 2
    assert books[0]["title"] == "Book B"
    assert books[1]["title"] == "Book A"

    assert main.cache.get(0, 100) == books