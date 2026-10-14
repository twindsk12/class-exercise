def validate_columns(df, required_columns):
    """Return the DataFrame if all required columns exist."""
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return df