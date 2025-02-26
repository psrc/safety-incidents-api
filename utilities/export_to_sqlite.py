import pandas as pd
import psrcelmerpy
import sqlite3 

sqlite_path = "./main/safety2.sqlite"

e_conn = psrcelmerpy.ElmerConn()
sqlite_conn =  sqlite3.connect(sqlite_path)

#tbls = ['incidents', 'vehicles', 'persons']
tbls = {'incidents' : 'incident', 'vehicles' : 'vehicle', 'persons' : 'person'}
# tbl_nm = 'vehicles'
for tbl_nm in tbls.keys():
    # out_tbl = f"safety.{tbl_nm}"
    query = f"""
        SELECT * 
        FROM safety.{tbl_nm} 
    """
    df = e_conn.get_query(query)
    df.to_sql(tbls[tbl_nm].capitalize(), sqlite_conn, if_exists='replace', index=False)
    rows_processed = len(df)
    print(f"Processed {rows_processed} rows for {tbl_nm}")


# Add indexes to improve query performance
print("Adding indexes to tables...")

# Indexes for incident table
print("Adding indexes to incident table...")
sqlite_conn.execute("CREATE INDEX idx_incident_collision_report_number ON incident(Collision_Report_Number)")
sqlite_conn.execute("CREATE INDEX idx_incident_city_name ON incident(City_Name)")

# Indexes for vehicle table
print("Adding indexes to vehicle table...")
sqlite_conn.execute("CREATE INDEX idx_vehicle_incident_rec_id ON vehicle(incident_rec_id)")
sqlite_conn.execute("CREATE INDEX idx_vehicle_collision_report_number ON vehicle(Collision_Report_Number)")

print("Indexes added successfully")
print(f"export completed for {sqlite_path}")

sqlite_conn.close()