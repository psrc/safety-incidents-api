from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class IncidentBase(SQLModel):
    #name: str = Field(index=True)
    #headquarters: str

    #incident_rec_id: int = Field(index=True)
    City_Name: str = Field()
    County_Name: str = Field()
    Latitude: float = Field()
    Longitude: float = Field()


class Incident(IncidentBase, table=True):
    #id: int | None = Field(default=None, primary_key=True)

    #heroes: list["Hero"] = Relationship(back_populates="team")
    
    incident_rec_id: int = Field(primary_key=True)
    City_Name: str = Field()

    vehicles: list["Vehicle"] = Relationship(back_populates="incident")


class IncidentCreate(IncidentBase):
    pass


class IncidentPublic(IncidentBase):
    #id: int

    incident_rec_id: int 


#class IncidentUpdate(SQLModel):
    # id: int | None = None
    # name: str | None = None
    # headquarters: str | None = None

    #Collision_Report_Number: str | None = None
    #name: str | None = None
    # headquarters: str | None = None



class VehicleBase(SQLModel):
    #name: str = Field(index=True)
    #secret_name: str
    #age: int | None = Field(default=None, index=True)

    #team_id: int | None = Field(default=None, foreign_key="team.id")
    #vehicle_rec_id: int = Field(index=True)
    Vehicle_Type: str = Field()
    Vehicle_Make: str = Field()
    Vehicle_Model: str = Field()
    Vehicle_Style: str = Field()
    

    incident_rec_id: int | None = Field(default=None, foreign_key="incident.incident_rec_id")


class Vehicle(VehicleBase, table=True):
    #id: int | None = Field(default=None, primary_key=True)

    #team: Team | None = Relationship(back_populates="heroes")

    vehicle_rec_id: int | None = Field(default=None, primary_key=True)

    incident: Incident | None = Relationship(back_populates="vehicles")



class VehiclePublic(VehicleBase):
    #id: int
    vehicle_rec_id: int


class VehicleCreate(VehicleBase):
    pass


# class VehicleUpdate(SQLModel):
#     name: str | None = None
#     secret_name: str | None = None
#     age: int | None = None
#     team_id: int | None = None


class VehiclePublicWithIncident(VehiclePublic):
    incident: IncidentPublic | None = None


class IncidentPublicWithVehicles(IncidentPublic):
    vehicles: list[VehiclePublic] = []


sqlite_file_name = "safety2.sqlite"
sqlite_url = f"sqlite:///C:/Stefan/safety-incidents-api/main/{sqlite_file_name}"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# @app.post("/vehicles/", response_model=VehiclePublic)
# def create_vehicle(*, session: Session = Depends(get_session), vehicle: VehicleCreate):
#     db_hero = Vehicle.model_validate(vehicle)
#     session.add(db_hero)
#     session.commit()
#     session.refresh(db_hero)
#     return db_hero


@app.get("/vehicles/", response_model=list[VehiclePublic])
def read_vehicles(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    vehicles = session.exec(select(Vehicle).offset(offset).limit(limit)).all()
    return vehicles


@app.get("/vehicle/{vehicle_rec_id}", response_model=VehiclePublicWithIncident)
def read_vehicle(*, session: Session = Depends(get_session), vehicle_rec_id: int):
    vehicle = session.get(Vehicle, vehicle_rec_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Hero not found")
    return vehicle


@app.get("/incidents/", response_model=list[IncidentPublic])
def read_incidents(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    incidents = session.exec(select(Incident).offset(offset).limit(limit)).all()
    return incidents

@app.get("/incidents/{City_Name}", response_model=list[IncidentPublicWithVehicles])
def read_incidents_by_city(*, City_Name: str, session: Session = Depends(get_session)):
    incidents = session.exec(select(Incident).where(Incident.City_Name==City_Name)).all()
    if not incidents:
        raise HTTPException(status_code=404, detail="Team not found")
    return incidents


@app.get("/incidents/{incident_rec_id}", response_model=IncidentPublicWithVehicles)
def read_incident(*, incident_rec_id: int, session: Session = Depends(get_session)):
    incident = session.get(Incident, incident_rec_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Team not found")
    return incident

