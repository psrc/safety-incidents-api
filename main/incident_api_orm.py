from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

class Incident(SQLModel, table=True):
    Collision_Report_Number: str = Field(primary_key=True)
    Latitude: float = Field()
    Longitude: float = Field()
    City_Name: str = Field()
    County_Name: str = Field()
    
    vehicles: list["Vehicle"] = Relationship(back_populates="incident")

class Vehicle(SQLModel, table=True):
    vehicle_rec_id: int = Field(primary_key=True)
    #vehicle_rec_id: int = Field(primary_key=True)
    Collision_Report_Number: str = Field(foreign_key="incident.Collision_Report_Number")
    #Collision_Report_Number: str = Field(primary_key=True)
    Vehicle_Type: str = Field()
    Vehicle_Make: str = Field()
    Vehicle_Model: str = Field()
    Vehicle_Style: str = Field()
    #team_id: int | None = Field(default=None, foreign_key="team.id")
    incident: Incident | None = Relationship(back_populates="vehicles")
    #incident_id: int | None = Field(default=None, foreign_key="Incident.Collision_Report_Number")


# class VehicleWithIncident(Vehicle):
#     incident: Incident | None = None 

# class IncidentWithVehicles(Incident):
#     vehicle: list[Vehicle] = []



# class Persons(SQLModel, table=True):
#     person_rec_id: int = Field(primary_key=True)
#     Collision_Report_Number: str = Field()
#     Age: float = Field()
#     Gender: float = Field()
#     Injury_Type: str = Field()

sqlite_file_name = "safety2.sqlite"
sqlite_url = f"sqlite:///C:/Stefan/safety-incidents-api/main/{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# @app.get("/incidents/")
# def read_incidents(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[Incidents]:
#     incidents = session.exec(select(Incidents).offset(offset).limit(limit)).all()
#     return incidents

@app.get("/incidents/", response_model=list[Incident])
def read_incidents(offset: int = 0, limit: int = Query(default=100, le=100)):
    with Session(engine) as session:
        incidents = session.exec(select(Incident).offset(offset).limit(limit)).all()
        return incidents
    

@app.get("/incidents/{Collision_Report_Number}", response_model=Incident)
def read_incident(Collision_Report_Number: str):
    with Session(engine) as session:
        incident = session.get(Incident, Collision_Report_Number)
        if not incident:
            raise HTTPException(status_code=404, detail="Hero not found")
        return incident

@app.get("/vehicles/", response_model=list[Vehicle])
def read_vehicles(offset: int = 0, limit: int = Query(default=100, le=100)):
    with Session(engine) as session:
        vehicles = session.exec(select(Vehicle).offset(offset).limit(limit)).all()
        return vehicles

@app.get("/vehicles/{vehicle_rec_id}", response_model=Vehicle)
def read_vehicle(vehicle_rec_id: str):
    with Session(engine) as session:
        vehicle = session.get(Vehicle,  vehicle_rec_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Hero not found")
        return vehicle
