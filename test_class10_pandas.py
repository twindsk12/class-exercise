#test_class10_pandas.py
import pandas as pd
import pytest

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "title": ["Movie A", "Movie B", "Movie C", "Movie D", "Movie D"],
        "type": ["Movie", "Movie", "Movie", "Movie", "Movie"],
        "release_year": [2020, 2021, 2022, 2023, 2023],
        "rating": [7, 8, 6, 9, 9],
    })

def test_invalid_numeric_value():
    df = pd.DataFrame({"rating": [7, "unknown", 9]})

    with pytest.raises(ValueError):
        pd.to_numeric(df["rating"])

def test_dataframe_shape(sample_df):
    assert sample_df.shape == (5, 4)

def test_drop_duplicates(sample_df):
    result = sample_df.drop_duplicates()
    assert result.shape == (4, 4)
    assert result["title"].tolist() == ["Movie A", "Movie B", "Movie C", "Movie D"]
