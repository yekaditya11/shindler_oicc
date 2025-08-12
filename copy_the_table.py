import psycopg2
from psycopg2 import sql
import pandas as pd
import os

# Method 1: Using psycopg2 with SQL commands (Recommended for large tables)
def copy_table_with_psycopg2(source_table, target_table, connection_params):
    """
    Copy a PostgreSQL table to a new table using SQL commands
    
    Args:
        source_table (str): Name of the source table
        target_table (str): Name of the target table
        connection_params (dict): Database connection parameters
    """
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Create new table with same structure and copy data
        copy_query = sql.SQL("""
            CREATE TABLE {target} AS 
            SELECT * FROM {source}
        """).format(
            target=sql.Identifier(target_table),
            source=sql.Identifier(source_table)
        )
        
        cursor.execute(copy_query)
        conn.commit()
        
        print(f"Successfully copied {source_table} to {target_table}")
        
        # Get row count
        cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(target_table)))
        row_count = cursor.fetchone()[0]
        print(f"Copied {row_count} rows")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

# Method 2: Copy structure first, then data (more control)
def copy_table_structure_and_data(source_table, target_table, connection_params):
    """
    Copy table structure first, then copy data separately
    """
    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Create table with same structure (no data)
        create_query = sql.SQL("""
            CREATE TABLE {target} AS 
            SELECT * FROM {source} 
            WHERE 1=0
        """).format(
            target=sql.Identifier(target_table),
            source=sql.Identifier(source_table)
        )
        
        cursor.execute(create_query)
        
        # Copy data
        insert_query = sql.SQL("""
            INSERT INTO {target} 
            SELECT * FROM {source}
        """).format(
            target=sql.Identifier(target_table),
            source=sql.Identifier(source_table)
        )
        
        cursor.execute(insert_query)
        conn.commit()
        
        print(f"Successfully copied structure and data from {source_table} to {target_table}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

# Method 3: Using pandas (good for smaller tables with data processing)
def copy_table_with_pandas(source_table, target_table, connection_params):
    """
    Copy table using pandas (useful for data transformation)
    """
    try:
        # Create connection string for pandas
        conn_string = f"postgresql://{connection_params['user']}:{connection_params['password']}@{connection_params['host']}:{connection_params['port']}/{connection_params['database']}"
        
        # Read source table
        df = pd.read_sql(f'SELECT * FROM {source_table}', conn_string)
        
        # Write to new table
        df.to_sql(target_table, conn_string, if_exists='replace', index=False)
        
        print(f"Successfully copied {len(df)} rows from {source_table} to {target_table}")
        
    except Exception as e:
        print(f"Error: {e}")

# Method 4: Copy with specific conditions/filters
def copy_table_with_conditions(source_table, target_table, connection_params, where_condition=""):
    """
    Copy table with optional WHERE condition
    """
    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        if where_condition:
            copy_query = sql.SQL("""
                CREATE TABLE {target} AS 
                SELECT * FROM {source} 
                WHERE {condition}
            """).format(
                target=sql.Identifier(target_table),
                source=sql.Identifier(source_table),
                condition=sql.SQL(where_condition)
            )
        else:
            copy_query = sql.SQL("""
                CREATE TABLE {target} AS 
                SELECT * FROM {source}
            """).format(
                target=sql.Identifier(target_table),
                source=sql.Identifier(source_table)
            )
        
        cursor.execute(copy_query)
        conn.commit()
        
        print(f"Successfully copied {source_table} to {target_table}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

# Example usage
if __name__ == "__main__":
    # Database connection parameters
    connection_params = {
        'host': "schindler-safetyconnect.ccgjylc7uxqb.us-east-1.rds.amazonaws.com",
        'database': "postgres",
        'user': "postgres",
        'password': "IxIKjgGrN46KOKLne06m",
        'port': "5432"
    }
    
    source_table = 'unsafe_events_srs_enriched'
    target_table = 'unsafe_events_srs_enriched_old'
    
    # Choose one of the methods:
    
    # Method 1: Simple copy (recommended)
    copy_table_with_psycopg2(source_table, target_table, connection_params)
    
    # Method 2: Copy structure then data
    # copy_table_structure_and_data(source_table, target_table, connection_params)
    
    # Method 3: Using pandas
    # copy_table_with_pandas(source_table, target_table, connection_params)
    
    # Method 4: Copy with conditions
    # copy_table_with_conditions(source_table, target_table, connection_params, "id > 100")