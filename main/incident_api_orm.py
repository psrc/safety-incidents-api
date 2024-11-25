from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Incidents(SQLModel, table=True):
    Collision_Report_Number: str = Field(primary_key=True)
    Latitude: float = Field()
    Longitude: float = Field()
    City_Name: str = Field()
    County_Name: str = Field()

class Vehicles(SQLModel, table=True):
    #vehicle_rec_id: int = Field(primary_key=True)
    Collision_Report_Number: str = Field(primary_key=True)
    Vehicle_Type: str = Field()
    Vehicle_Make: str = Field()
    Vehicle_Model: str = Field()
    Vehicle_Style: str = Field()

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

@app.get("/incidents/")
def read_incidents(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Incidents]:
    incidents = session.exec(select(Incidents).offset(offset).limit(limit)).all()
    return incidents

@app.get("/incidents/{Collision_Report_Number}")
def read_incident(Collision_Report_Number: str, session: SessionDep) -> Incidents:
    incident = session.get(Incidents, Collision_Report_Number)
    if not incident:
        raise HTTPException(status_code=404, detail="Hero not found")
    return incident

@app.get("/vehicles/")
def read_vehicles(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Vehicles]:
    vehicles = session.exec(select(Vehicles).offset(offset).limit(limit)).all()
    return vehicles

@app.get("/vehicles/{Report_Number}")
def read_vehicle(Report_Number: str, session: SessionDep) -> Vehicles:
    vehicle = session.get(Vehicles, Report_Number)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Hero not found")
    return vehicle