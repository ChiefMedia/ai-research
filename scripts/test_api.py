from google import genai
from pathlib import Path
import polars as pl
import psycopg2
from typing import Optional
import yaml



GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY"


def get_config():
    # Construct a Path object representing the parent directory
    parent_dir = Path(".").resolve().parent

    # Construct a Path object representing the file in the parent directory
    file_path = parent_dir / "config.yaml"

    # Open and read the file
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def make_request(request_text, api_key=None):
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=request_text
    )
    return response.text


def query_to_polars(
    query: str,
    db_url: str,
    db_name: str, 
    db_user: str,
    db_password: str,
    port: int = 5432
) -> pl.DataFrame:
    """
    Execute a PostgreSQL query and return the results as a Polars DataFrame.
    
    Parameters:
    -----------
    query : str
        The SQL query to execute
    db_url : str
        The database server URL or hostname
    db_name : str
        The name of the database
    db_user : str
        The username for database authentication
    db_password : str
        The password for database authentication
    port : int, optional
        The database server port (default: 5432)
    
    Returns:
    --------
    pl.DataFrame
        A Polars DataFrame containing the query results
    
    Raises:
    -------
    Exception
        If there's an error connecting to the database or executing the query
    """
    conn = None
    cursor = None
    
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=db_url,
            database=db_name,
            user=db_user,
            password=db_password,
            port=port
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in cursor.description]
        
        # If there are no results, return an empty DataFrame with the columns
        if not rows:
            return pl.DataFrame(schema=[(name, pl.Utf8) for name in column_names])
        
        # Create a Polars DataFrame from the results
        df = pl.DataFrame(rows, schema=column_names)
        
        return df
    
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")
    
    finally:
        # Close cursor and connection in the finally block
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def main():
    config = get_config()

    data = query_to_polars(
        "SELECT * FROM web_visit_results LIMIT 5",
        db_url=config["RFI_PROD_SERVER"],
        db_name=config["RFI_PROD_DB"],
        db_user=config["RFI_PROD_USER"],
        db_password=config["RFI_PROD_PWD"]
    )
    print(data)

    request_text = """
    Explain why Manchester United are a declining team.
    """
    
    #make_request(request_text, api_key=config["GEMINI_KEY"])


if __name__ == "__main__":
    main()