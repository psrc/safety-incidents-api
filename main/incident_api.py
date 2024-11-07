
from fastapi import FastAPI, HTTPException
import pandas as pd
import sqlite3

app  = FastAPI()


def get_db_connection():
    return sqlite3.connect("safety.sqlite")


@app.get("/")
def root():
    return {"message": "WSDOT Safety Incident Data API"}


@app.get("/incidents")
async def get_incidents():
    with get_db_connection() as s_conn:
        qry = """
            select i.Collision_report_number, i.incident_date
            from incidents as i
        """
        df = pd.read_sql(qry, s_conn)
        return df.to_dict(orient='records')
    
    
@app.get("/vehicles/{collision_report_number}")
async def get_vehicles_by_id(collision_report_number: str):

    with get_db_connection() as s_conn:
        try:
            qry = f"""
                    select i.Collision_report_number, i.incident_date
                    from incidents as i
                    where i.Collision_Report_number = ?
                """
            df_incident = pd.read_sql(qry, s_conn, params=[collision_report_number])
            
            qry = f"""
                select v.unit_number, v.Vehicle_Type 
                from incidents as i 
                    join vehicles as v on i.incident_rec_id = v.incident_rec_id 
                    where i.Collision_Report_number = ?
                """
            df_vehicles = pd.read_sql(qry, s_conn, params=[collision_report_number])
            
            structured_data = {
                'incident': df_incident.to_dict(orient='records')[0],
                'vehicles': df_vehicles.to_dict(orient='records')
            }
            
            return structured_data

        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving vehicle data")
    

@app.get("/persons/{collision_report_number}")
async def get_persons_by_id(collision_report_number: str):

    with get_db_connection() as s_conn:
        try:

            qry_incident = f"""
                select i.Collision_report_number, i.incident_date
                from incidents as i
                where i.Collision_Report_number = ?
                """
            df_incident = pd.read_sql(qry_incident, s_conn, params=[collision_report_number])
            
            qry_person = f"""
                select p.Involved_Person_Type, p.Age, p.Gender
                from incidents as i 
                    join vehicles as v on i.incident_rec_id = v.incident_rec_id 
                    join persons as p on v.vehicle_rec_id = p.vehicle_rec_id
                where i.Collision_Report_number = ?
                """
            df_person = pd.read_sql(qry_person, s_conn, params=[collision_report_number])

            structured_data = {
                'incident': df_incident.to_dict(orient='records')[0],
                'persons': df_person.to_dict(orient='records')
            }
            return structured_data
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving person data")