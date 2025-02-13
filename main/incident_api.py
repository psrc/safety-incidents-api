
from fastapi import Depends, FastAPI, HTTPException, Query
# from typing import Optional, Dict, Type, List
# import pandas as pd
# import sqlite3
# from typing import Annotated
# from sqlalchemy import Column, Integer, String, DateTime, create_engine, inspect, MetaData, Table
#from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


def get_db_connection():
    sqlite_file_name = "safety2.sqlite"
    sqlite_url = f"sqlite:///{sqlite_file_name}?mode=ro"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    # metadata = MetaData()
    # metadata.reflect(bind=engine)
    return engine#, metadata

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


#engine, metadata = get_db_connection()
sqlite_file_name = "safety2.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}?mode=ro"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
#engine= get_db_connection()


def get_session():
    #session = SessionLocal()
    try:
        with Session(engine) as session:
            yield session
    finally:
        session.close()

class IncidentBase(SQLModel):
    City_Name: str = Field()
    County_Name: str = Field()
    Latitude: float = Field()
    Longitude: float = Field()

class Incident(IncidentBase, table=True):
    incident_rec_id: int = Field(primary_key=True)
    City_Name: str = Field()
    # Collision_Report_Number: str = Field()
    Incident_Date: str = Field()

    vehicles: list["Vehicle"] = Relationship(back_populates="incident")

class IncidentCreate(IncidentBase):
    pass

class IncidentPublic(IncidentBase):
    incident_rec_id: int
    

class VehicleBase(SQLModel):
    unit_number: int = Field()
    Vehicle_Type: str = Field()

    # incident_rec_id: Optional[int] = Field(default=None, foreign_key="incident.incident_rec_id")
    incident_rec_id: int | None = Field(default=None, foreign_key="incident.incident_rec_id")

class Vehicle(VehicleBase, table=True):
    vehicle_rec_id: int | None = Field(primary_key=True)
    #Collision_Report_Number: Optional[str] = Field(default=None, foreign_key="Incident.Collision_Report_Number")
    # incident: Optional[Incident] = Relationship(back_populates="vehicles")
    incident: Incident | None = Relationship(back_populates="vehicles")


class VehiclePublic(VehicleBase):
    vehicle_rec_id: int


class VehiclePublicWithIncident(VehiclePublic):
    incident: IncidentPublic | None = None


class IncidentPublicWithVehicles(IncidentPublic):
    #incident_rec_id: int
    # Incident_Date: str
    # vehicles: List["Vehicle"] = Relationship(back_populates="incident")
    vehicles: list[VehiclePublic] = []

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


# @app.get("/incidents_by_city/{city_name}", response_model=list[IncidentPublicWithVehicles])
# async def get_incidents_by_city(city_name: str):
#     with Session(engine) as session:
#         statement = select(Incident).where(Incident.City_Name == city_name)
#         results = session.exec(statement)
#         return results.all()
    
@app.get("/incidents_by_city/{City_Name}", response_model=IncidentPublicWithVehicles)
def get_incidents_by_city(*, City_Name: str, session: Session = Depends(get_session)):
    results = session.exec(select(Incident).where(Incident.City_Name==City_Name)).first()
    if not results:
        raise HTTPException(status_code=404, detail="No Incidents found")
    return results
