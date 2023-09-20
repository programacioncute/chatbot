import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import sqlalchemy
import psycopg2
from psycopg2 import pool

## ntt123_dev


host = "c-rg-cosmosdb-dev.4u3hxce4ykembm.postgres.cosmos.azure.com"
dbname = "profuturo"
user = "citus"
password = "ntt123_dev"
sslmode = "require"

# Build a connection string from the variables
conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)

postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20,conn_string)
if (postgreSQL_pool):
    print("Connection pool created successfully")


conn = postgreSQL_pool.getconn()
cursor = conn.cursor()

#cursor.execute("SELECT distinct(categoria) FROM change_request;")
#cursor.execute("SELECT COUNT(numero) AS Numero_de_tickets FROM change_request WHERE area = 'Soporte Tecnico';")
cursor.execute("SELECT DISTINCT(area) FROM change_request")
rows = cursor.fetchall()
# Print all rows
for row in rows:
    print(row)
    #print("Data row = (%s, %s)" %(str(row[0]), str(row[1])))