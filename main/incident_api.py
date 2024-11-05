
from fastapi import FastAPI, HTTPException
import pandas as pd
import sqlite3

app  = FastAPI()

s_conn = sqlite3.connect("safety.sqlite")

@app.get("/")
def root():
    return {"message": "WSDOT Safety Incident Data API"}

    
@app.get("/vehicles/{incident_rec_id}")
async def get_vehicles_by_id(incident_rec_id: int):
    qry = f"""
        select i.Collision_report_number, v.Vehicle_Type 
        from incidents as i 
            join vehicles as v on i.incident_rec_id = v.incident_rec_id 
        where i.incident_rec_id = {incident_rec_id}
        """
    df = pd.read_sql(qry, s_conn)
    return df.to_json(force_ascii=True)
    
@app.get("/persons/{incident_rec_id}")
async def get_persons_by_id(incident_rec_id: int):
    try:

        qry_incident = f"""
            select i.Collision_report_number, i.incident_date
            from incidents as i
            where i.incident_rec_id = {incident_rec_id}
            """
        df_incident = pd.read_sql(qry_incident, s_conn)
        
        qry_person = f"""
            select p.Involved_Person_Type, p.Age, p.Gender
            from incidents as i 
                join vehicles as v on i.incident_rec_id = v.incident_rec_id 
                join persons as p on v.vehicle_rec_id = p.vehicle_rec_id
            where i.incident_rec_id = {incident_rec_id}
            """
        df_person = pd.read_sql(qry_person, s_conn)

        structured_data = {
            'incident': df_incident.to_dict(orient='records')[0],
            'persons': df_person.to_dict(orient='records')
        }
        return structured_data
    
    except:
        print("Something went wrong in get_person_by_id")