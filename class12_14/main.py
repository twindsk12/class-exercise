#main.py
import io
import logging
from pathlib import Path
from src import ProcessConfig

import pandas as pd
from fastapi import FastAPI, Query, File, HTTPException, UploadFile
from src import MovieInput
from src import MovieResponse
from src import MovieInput, MovieResponse, CSVInfo, DataStorage
from middleware import log_requests



app = FastAPI(title="Movie API")

app.middleware("http")(log_requests)

@app.get("/health")
def health_check():
    return {"status": "ok"}

#a path parameter identifies a resource (movie) to retrieve
@app.get("/demo/movies/{movie_id}")
def demo_get_movie(movie_id: int): #type annotation: it declares the expected type, int
    return {"requested_id": movie_id}

#a query parameter adjusts a request
@app.get("/demo/movies")
def demo_list_movies(limit: int = Query(default=2, ge=1)):
    #The default is 2 when limit is omitted in the query.
    # ge=1 means greater than or equal to one.
    return {"requested_limit": limit}

@app.post("/demo/movies")
def demo_add_movie(movie: MovieInput):
    return movie.model_dump() #Converts the model to a Python dictionary.

demo_movie_examples = []

@app.post("/demo/movie-examples", response_model=MovieResponse)
def demo_add_movie_example(movie: MovieInput):
    movie_id = len(demo_movie_examples) + 1
    record = movie.model_dump()
    record["id"] = movie_id
    demo_movie_examples.append(record)
    return record

#main.py
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

movies = {
    1: {"id": 1, "title": "Movie A", "release_year": 2020},
    2: {"id": 2, "title": "Movie B", "release_year": 2021},
}

storage = DataStorage()

@app.get("/movies", response_model=list[MovieResponse])
def list_movies(limit: int = Query(default=2, ge=1)):
    # TODO 1: return up to limit movies as a list.
    # Log the number returned at INFO.
    # hint: movies is a dictionary whose values are movie records.
    result = list(movies.values())[:limit]

    logger.info("Returned %s movies", len(result))

    return result


@app.post("/movies", response_model=MovieResponse)
def add_movie(movie: MovieInput):
    # TODO 2:
    # Convert movie to a dictionary, add the new ID, and store it.
    # Log the new ID at INFO and return the stored record.
    movie_id = max(movies.keys(), default=0) + 1

    record = movie.model_dump()
    record["id"] = movie_id

    movies[movie_id] = record

    logger.info("Added movie: id=%s", movie_id)

    return record

@app.post("/inspect-csv", response_model=CSVInfo)
async def inspect_csv(file: UploadFile = File(...)):
    # TODO 2: check the filename extension using pathlib.
    # Reject non-CSV files with status 400 and log a WARNING.

    # TODO 3: await the file contents and parse the CSV.
    # Catch expected parsing/decoding errors (e.g. EmptyDataError,ParserError, UnicodeDecodeError) and raise HTTPException
    # with status_code=400.

    # TODO 4: save the DataFrame with storage.save_data().
    # Log the dataset ID, filename at INFO.
    # Return a CSVInfo object with the ID, filename, shape, and column names.
    if Path(file.filename or "").suffix.lower() != ".csv":
        logger.warning("Not a CSV file: %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV"
        )

    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ) as error:
        logger.warning("Cannot read CSV: %s", error)
        raise HTTPException(
            status_code=400,
            detail="Cannot read the uploaded CSV"
        )

    dataset_id = storage.save_data(df, file.filename)

    logger.info(
        "Stored CSV: id=%s, filename=%s",
        dataset_id,
        file.filename
    )

    return CSVInfo(
        filename=file.filename,
        rows=df.shape[0],
        columns=df.shape[1],
        column_names=df.columns.tolist(),
        dataset_id=dataset_id
    )

@app.get("/datasets/{dataset_id}/shape")
def get_dataset_shape(dataset_id: int):
    # TODO 5: get the DataFrame using storage.get_data().
    # If it is missing, log a WARNING and raise HTTPException with status 404.
    # Otherwise, log successful retrieval at INFO.
    # Return a dictionary with dataset_id, rows, and columns.
    df = storage.get_data(dataset_id)

    if df is None:
        logger.warning("Dataset not found: %s", dataset_id)
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    logger.info("Retrieved dataset shape: id=%s", dataset_id)

    return {
        "dataset_id": dataset_id,
        "rows": df.shape[0],
        "columns": df.shape[1]
    }


@app.post("/demo/process-config")
def demo_process_config(config: ProcessConfig):
    df = pd.DataFrame({
        "title": ["Movie A", "Movie A", "Movie B", None]
    })

    settings = config.model_dump()

    if settings["processing"]["remove_duplicates"]:
        df = df.drop_duplicates()

    if settings["processing"]["drop_missing"]:
        df = df.dropna()

    return {"rows": len(df)}