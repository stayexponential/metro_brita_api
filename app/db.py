# app/db.py

import pymssql

def get_db_connection():
    server = "192.168.0.5\\BRITAXL"
    port = 1433
    user = "sa"
    password = "P@ssw0rd"
    database = "POS_TEST_S31"

    try:
        # Use instance in the connection string
        connection = pymssql.connect(
            server=server,
            user=user,
            password=password,
            database=database,
            port=port,  # Optional if using a static port
        )
        return connection
    except pymssql.InterfaceError as e:
        print(f"Interface error connecting to SQL Server: {e}")
        raise
    except pymssql.DatabaseError as e:
        print(f"Database error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise