import polars as pl
import psycopg2
from chiefai.utils import get_config

def query(
    query: str,
    db_url: str = None,
    db_name: str = None,
    db_user: str = None,
    db_password: str = None,
    port: int = None,
    config_section: str = "DATABASE"  # Changed to uppercase
) -> pl.DataFrame:
    """
    Execute a PostgreSQL query and return the results as a Polars DataFrame.
    
    The function will use credentials from the config.yaml file in the ai-research
    root directory if they are not explicitly provided.
    
    Parameters:
    -----------
    query : str
        The SQL query to execute
    db_url : str, optional
        The database server URL or hostname. If None, read from config.
    db_name : str, optional
        The name of the database. If None, read from config.
    db_user : str, optional
        The username for database authentication. If None, read from config.
    db_password : str, optional
        The password for database authentication. If None, read from config.
    port : int, optional
        The database server port. If None, read from config or use default 5432.
    config_section : str, optional
        The section in the config file containing database credentials (default: "DATABASE")
    
    Returns:
    --------
    pl.DataFrame
        A Polars DataFrame containing the query results
    
    Raises:
    -------
    Exception
        If there's an error connecting to the database or executing the query
    """
    # Read config if any credential is not provided
    if any(param is None for param in [db_url, db_name, db_user, db_password, port]):
        try:
            config = get_config()
            db_config = config.get(config_section, {})
            
            # Use config values for any None parameters with uppercase keys
            db_url = db_url or db_config.get('URL')
            db_name = db_name or db_config.get('NAME')
            db_user = db_user or db_config.get('USER')
            db_password = db_password or db_config.get('PASSWORD')
            port = port or db_config.get('PORT', 5432)
            
        except Exception as e:
            raise Exception(f"Error reading database configuration: {str(e)}")
    
    # Validate that we have all required credentials
    missing = []
    if not db_url: missing.append("db_url")
    if not db_name: missing.append("db_name")
    if not db_user: missing.append("db_user")
    if not db_password: missing.append("db_password")
    
    if missing:
        raise ValueError(f"Missing required database credentials: {', '.join(missing)}")
    
    # Ensure port is an integer
    port = int(port)
    
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
        df = pl.DataFrame(rows, schema=column_names, orient="row")
        
        return df
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")
    finally:
        # Close cursor and connection in the finally block
        if cursor:
            cursor.close()
        if conn:
            conn.close()