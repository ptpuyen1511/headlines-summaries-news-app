from sqlalchemy import text
import pandas as pd

def read_all(conn):
    query = text('SELECT * FROM news')
    res = conn.execute(query)
    return pd.DataFrame(res.fetchall(), columns=res.keys())

