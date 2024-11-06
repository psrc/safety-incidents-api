
from fastapi import FastAPI, HTTPException
import pandas as pd
import sqlite3

app  = FastAPI()

s_conn = sqlite3.connect("safety.sqlite")

@app.get("/")
def root():
    return {"message": "WSDOT Safety Incident Data API"}

    
@app.get("/vehicles/{collision_report_number}")
async def get_vehicles_by_id(collision_report_number: str):

    try:
        qry = f"""
                select i.Collision_report_number, i.incident_date
                from incidents as i
                where i.Collision_Report_number = '{collision_report_number}'
            """
        df_incident = pd.read_sql(qry, s_conn)
        
        qry = f"""
            select v.unit_number, v.Vehicle_Type 
            from incidents as i 
                join vehicles as v on i.incident_rec_id = v.incident_rec_id 
                where i.Collision_Report_number = '{collision_report_number}'
            """
        df_vehicles = pd.read_sql(qry, s_conn)
        
        structured_data = {
            'incident': df_incident.to_dict(orient='records')[0],
            'vehicles': df_vehicles.to_dict(orient='records')
        }
        
        return structured_data

    except:
        print("Something went wrong in get_vehicles_by_id")
    

@app.get("/persons/{collision_report_number}")
async def get_persons_by_id(collision_report_number: str):
    try:

        qry_incident = f"""
            select i.Collision_report_number, i.incident_date
            from incidents as i
            where i.Collision_Report_number = '{collision_report_number}'
            """
        df_incident = pd.read_sql(qry_incident, s_conn)
        
        qry_person = f"""
            select p.Involved_Person_Type, p.Age, p.Gender
            from incidents as i 
                join vehicles as v on i.incident_rec_id = v.incident_rec_id 
                join persons as p on v.vehicle_rec_id = p.vehicle_rec_id
            where i.Collision_Report_number = '{collision_report_number}'
            """
        df_person = pd.read_sql(qry_person, s_conn)

        structured_data = {
            'incident': df_incident.to_dict(orient='records')[0],
            'persons': df_person.to_dict(orient='records')
        }
        return structured_data
    
    except:
        print("Something went wrong in get_person_by_id")