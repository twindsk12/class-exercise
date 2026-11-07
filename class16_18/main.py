import logging

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from check_storage import BookStorage

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class BookInput(BaseModel):
    title: str
    price: float = Field(ge=0)


class BookResponse(BookInput):
    id: int


app = FastAPI(title="Books Database API")
storage = BookStorage()


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    book = storage.get_book(book_id)
    if book is None:
        logger.warning(f"Book not found: {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    logger.info(f"Retrieved book: id={book_id}")
    return book

# GET: List books
@app.post("/books", response_model=BookResponse)
def add_book(book: BookInput):
    book_id = storage.add_book(book.title, book.price)

    logger.info(f"Added book: id={book_id}")

    return storage.get_book(book_id)


# GET: Search books by price range
@app.get("/books", response_model=list[BookResponse])
def list_books(
    min_price: float = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1)
):
    books = storage.list_books(
        min_price=min_price,
        limit=limit
    )

    logger.info(f"Returned {len(books)} books")
    return books


@app.get("/search/books", response_model=list[BookResponse])
def search_books(
    min_price: float = Query(ge=0),
    max_price: float = Query(ge=0)
):
    # TODO: if min_price > max_price, log WARNING and raise HTTPException
    # with status 400 and detail (e.g., "min_price must not exceed max_price").
    # Otherwise, call storage.search_books().
    # Log the returned row count at INFO and return the list.
    if min_price > max_price:
        logger.warning(
            f"Invalid price range: {min_price} to {max_price}"
        )

        raise HTTPException(
            status_code=400,
            detail="min_price must not exceed max_price"
        )

    books = storage.search_books(min_price, max_price)

    logger.info(f"Search returned {len(books)} books")

    return books
