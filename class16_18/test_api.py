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
    #`monkeypatch` makes the API use that test's storage object and restores the original afterward
    monkeypatch.setattr(main, "storage", storage)
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