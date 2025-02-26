import pandas as pd
import psrcelmerpy
import sqlite3 

sqlite_path = "./main/safety.sqlite"

e_conn = psrcelmerpy.ElmerConn()
sqlite_conn =  sqlite3.connect(sqlite_path)

tbls = {
    'incident': ['incident_rec_id', 'Collision_Report_Number', 'incident_date', 'City_Name', 'County_Name'],
    'vehicle': ['vehicle_rec_id', 'incident_rec_id', 'unit_number', 'Vehicle_Type', 'Collision_Report_Number'],
    'person': ['person_rec_id', 'Involved_Person_Type', 'Age', 'Gender']
}

primary_keys = {
    'incident': 'incident_rec_id',
    'vehicle': 'vehicle_rec_id',
    'person': 'person_rec_id'
}

foreign_keys = {
    'vehicle': {'incident': 'incident_rec_id'}
}

source_tables = {'incident': 'Incidents', 'vehicle': 'Vehicles', 'person': 'Persons'}

# tbl_nm = 'vehicles'
def export():
    try: 
        print("entered export")
        pks = primary_keys
        for tbl_nm in tbls.keys():
            print(f"exporting table {tbl_nm}...")
            # out_tbl = f"safety.{tbl_nm}"
            t_nm = source_tables[tbl_nm]
            columns = ','.join(tbls[tbl_nm])
            query = f"""
                SELECT {columns}
                FROM safety.{t_nm} 
            """
            df = e_conn.get_query(query)
            # dtype_clause = f"'{pks[tbl_nm]}': 'INTEGER PRIMARY KEY AUTOINCREMENT'"
            df.to_sql(tbl_nm, sqlite_conn, if_exists='replace', index=False, dtype={pks[tbl_nm]: 'INTEGER PRIMARY KEY AUTOINCREMENT'})
            #df.to_sql(tbl_nm, sqlite_conn, if_exists='replace', index=False)
            rows_processed = len(df)
            print(f"Processed {rows_processed} rows for {tbl_nm}")

        print(f"export completed for {sqlite_path}")

    except Exception as e:
        print(f"exception in export routine: {e.args[0]}")

export()

sql = """alter table vehicle rename to vehicle_bak"""
sqlite_conn.execute(sql)

sql = """CREATE TABLE vehicle (
    vehicle_rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_rec_id INTEGER,
    unit_number TEXT,
    Vehicle_Type TEXT,
    Collision_Report_Number TEXT,
    FOREIGN KEY (incident_rec_id) REFERENCES incidents (incident_rec_id)
)"""
sqlite_conn.execute(sql)

sql = """INSERT INTO vehicle (vehicle_rec_id, incident_rec_id, unit_number, Vehicle_Type, Collision_Report_Number)
    SELECT vehicle_rec_id, incident_rec_id, unit_number, Vehicle_Type, Collision_Report_Number
    from vehicle_bak
    """
sqlite_conn.execute(sql)

sql = """drop table vehicle_bak"""
sqlite_conn.execute(sql)

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

sqlite_conn.close()
