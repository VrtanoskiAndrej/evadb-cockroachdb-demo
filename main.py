# Import the EvaDB package
import evadb

# Connect to EvaDB and get a database cursor for running queries
cursor = evadb.connect().cursor()

params = {
    "user": "eva",
    "password": "password",
    "host": "localhost",
    "port": "26257",
    "database": "evadb",
}

query = f"CREATE DATABASE cockroachdb_data WITH ENGINE = 'cockroachdb', PARAMETERS = {params};"
print(cursor.query(query).df())
