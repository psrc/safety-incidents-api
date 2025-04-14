import pandas as pd
import psrcelmerpy
import sqlite3 

sqlite_path = "./main/safety.sqlite"

e_conn = psrcelmerpy.ElmerConn()
sqlite_conn =  sqlite3.connect(sqlite_path)

tbls = {
    'Incident': ['incident_rec_id', 'Collision_Report_Number', 'incident_date', 'City_Name', 'County_Name', 'Latitude', 'Longitude'],
    'Vehicle': ['vehicle_rec_id', 'incident_rec_id', 'unit_number', 'Vehicle_Type', 'Collision_Report_Number', 'Vehicle_Make', 'Vehicle_Model', 'Vehicle_Style'],
    'Person': ['person_rec_id', 'vehicle_rec_id', 'Collision_Report_Number', 'Involved_Person_Type', 'Age', 'Gender', 'Injury_Type', 'Impairment_Status']
}

primary_keys = {
    'Incident': 'incident_rec_id',
    'Vehicle': 'vehicle_rec_id',
    'Person': 'person_rec_id'
}

foreign_keys = {
    'Vehicle': {'Incident': 'incident_rec_id'}
}

source_tables = {'Incident': 'Incidents', 'Vehicle': 'Vehicles', 'Person': 'Persons'}

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

sql = """alter table Vehicle rename to vehicle_bak"""
sqlite_conn.execute(sql)

sql = """CREATE TABLE Vehicle (
    vehicle_rec_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_rec_id INTEGER,
    unit_number TEXT,
    Vehicle_Type TEXT,
    Collision_Report_Number TEXT,
    Vehicle_Make TEXT,
    Vehicle_Model TEXT,
    Vehicle_Style TEXT,
    FOREIGN KEY(incident_rec_id) REFERENCES Incidents (incident_rec_id)
)"""
sqlite_conn.execute(sql)

print("copying data from vehicle_bak to Vehicle")
sql = """INSERT INTO Vehicle (vehicle_rec_id, incident_rec_id, unit_number, Vehicle_Type, Collision_Report_Number, Vehicle_Make, Vehicle_Model, Vehicle_Style)
    SELECT vehicle_rec_id, incident_rec_id, unit_number, Vehicle_Type, Collision_Report_Number, Vehicle_Make, Vehicle_Model, Vehicle_Style
    from vehicle_bak"""
sqlite_conn.execute(sql)
sqlite_conn.commit()  # Commit the transaction to save the data
print("...finished")

sql = """drop table vehicle_bak"""
sqlite_conn.execute(sql)
sqlite_conn.commit()  # Commit the transaction to drop the table

# Add indexes to improve query performance
print("Adding indexes to tables...")

# Indexes for incident table
print("Adding indexes to Incident table...")
sqlite_conn.execute("CREATE INDEX idx_incident_collision_report_number ON Incident(Collision_Report_Number)")
sqlite_conn.execute("CREATE INDEX idx_incident_city_name ON Incident(City_Name)")

# Indexes for vehicle table
print("Adding indexes to Vehicle table...")
sqlite_conn.execute("CREATE INDEX idx_vehicle_incident_rec_id ON Vehicle(incident_rec_id)")
sqlite_conn.execute("CREATE INDEX idx_vehicle_collision_report_number ON Vehicle(Collision_Report_Number)")
sqlite_conn.commit()  # Commit the transaction to save the indexes

print("Indexes added successfully")

sqlite_conn.close()
