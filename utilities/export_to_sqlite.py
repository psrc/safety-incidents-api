import pandas as pd
import psrcelmerpy
import sqlite3 

sqlite_path = "./main/safety2.sqlite"

e_conn = psrcelmerpy.ElmerConn()
sqlite_conn =  sqlite3.connect(sqlite_path)

tbls = ['incidents', 'vehicles', 'persons']
# tbl_nm = 'vehicles'
for tbl_nm in tbls:
    # out_tbl = f"safety.{tbl_nm}"
    query = f"""
        SELECT * 
        FROM safety.{tbl_nm} 
    """
    df = e_conn.get_query(query)
    df.to_sql(tbl_nm, sqlite_conn, if_exists='replace', index=False)
    rows_processed = len(df)
    print(f"Processed {rows_processed} rows for {tbl_nm}")

print(f"export completed for {sqlite_path}")

sqlite_conn.close()