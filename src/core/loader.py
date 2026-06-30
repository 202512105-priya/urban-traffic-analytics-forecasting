import pandas as pd

def load_csv(file_path: str) -> pd.DataFrame:
    """
    TODO: Load a CSV dataset from the local filesystem.
    
    Args:
        file_path (str): Path to the target CSV file.
    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    raise NotImplementedError("load_csv() is not implemented yet in src/core/loader.py.")

def load_postgres(connection_uri: str, query: str) -> pd.DataFrame:
    """
    TODO: Query a PostgreSQL database and return a DataFrame.
    
    Args:
        connection_uri (str): PostgreSQL database URI.
        query (str): SQL select query to execute.
    Returns:
        pd.DataFrame: Query result DataFrame.
    """
    raise NotImplementedError("load_postgres() is not implemented yet in src/core/loader.py.")
