
from fastapi import Depends, FastAPI, HTTPException, Query
from typing import Optional, Dict, Type, List
import pandas as pd
import sqlite3
from typing import Annotated
from sqlalchemy import Column, Integer, String, DateTime, create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


def get_db_connection():
    sqlite_file_name = "safety5.sqlite"
    sqlite_url = f"sqlite:///{sqlite_file_name}?mode=ro"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return engine, metadata

def get_pk(table_name: str):
    """
    return the primary key column for a table
    """
    pk_dict = {
        'incident': 'incident_rec_id',
        'vehicle': 'vehicle_rec_id',
        'person': 'person_rec_id'
    }
    return pk_dict[table_name]


engine, metadata = get_db_connection()


def get_session():
    #session = SessionLocal()
    try:
        with Session(engine) as session:
            yield session
    finally:
        session.close()


class Incident(SQLModel, table=True):
    incident_rec_id: int = Field(primary_key=True)
    Collision_Report_Number: str = Field()
    incident_date: str = Field()
    City_Name: str = Field()

    vehicles: List["Vehicle"] = Relationship(back_populates="incident")

class Vehicle(SQLModel, table=True):
    vehicle_rec_id: int = Field(primary_key=True)
    unit_number: int = Field()
    Vehicle_Type: str = Field()

    incident_rec_id: Optional[int] = Field(default=None, foreign_key="incident.incident_rec_id")
    #Collision_Report_Number: Optional[str] = Field(default=None, foreign_key="Incident.Collision_Report_Number")
    incident: Optional[Incident] = Relationship(back_populates="vehicles")


app  = FastAPI()

@app.get("/")
def root():
    return {"message": "WSDOT Safety Incident Data API"}

@app.get("/incidents/{Collision_Report_Number}", response_model=Incident)
async def get_incident(Collision_Report_Number: str):
    with Session(engine) as session:
        incidents = session.get(Incident, Collision_Report_Number)
        if not incidents:
            raise HTTPException(status_code=404, detail="No Incidents found")
        return incidents


@app.get("/incidents_by_city/{city_name}", response_model=List[Incident])
async def get_incidents_by_city(city_name: str):
    with Session(engine) as session:
        statement = select(Incident).where(Incident.City_Name == city_name)
        results = session.exec(statement)
        return results.all()
    
# @app.get("/vehicles/{collision_report_number}")
# async def get_vehicles_by_id(collision_report_number: str):

#     with get_db_connection() as s_conn:
#         try:
#             qry = f"""
#                     select i.Collision_report_number, i.incident_date
#                     from incidents as i
#                     where i.Collision_Report_number = ?
#                 """
#             df_incident = pd.read_sql(qry, s_conn, params=[collision_report_number])
            
#             qry = f"""
#                 select v.unit_number, v.Vehicle_Type 
#                 from incidents as i 
#                     join vehicles as v on i.incident_rec_id = v.incident_rec_id 
#                     where i.Collision_Report_number = ?
#                 """
#             df_vehicles = pd.read_sql(qry, s_conn, params=[collision_report_number])
            
#             structured_data = {
#                 'incident': df_incident.to_dict(orient='records')[0],
#                 'vehicles': df_vehicles.to_dict(orient='records')
#             }
            
#             return structured_data

#         except Exception as e:
#             raise HTTPException(status_code=500, detail="Error retrieving vehicle data")
    

# @app.get("/persons/{collision_report_number}")
# async def get_persons_by_id(collision_report_number: str):

#     with get_db_connection() as s_conn:
#         try:

#             qry_incident = f"""
#                 select i.Collision_report_number, i.incident_date
#                 from incidents as i
#                 where i.Collision_Report_number = ?
#                 """
#             df_incident = pd.read_sql(qry_incident, s_conn, params=[collision_report_number])
            
#             qry_person = f"""
#                 select p.Involved_Person_Type, p.Age, p.Gender
#                 from incidents as i 
#                     join vehicles as v on i.incident_rec_id = v.incident_rec_id 
#                     join persons as p on v.vehicle_rec_id = p.vehicle_rec_id
#                 where i.Collision_Report_number = ?
#                 """
#             df_person = pd.read_sql(qry_person, s_conn, params=[collision_report_number])

#             structured_data = {
#                 'incident': df_incident.to_dict(orient='records')[0],
#                 'persons': df_person.to_dict(orient='records')
#             }
#             return structured_data
        
#         except Exception as e:
#             raise HTTPException(status_code=500, detail="Error retrieving person data")