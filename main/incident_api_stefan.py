from fastapi import Depends, FastAPI, HTTPException, Query, APIRouter, Response, Request
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
import time
import pandas as pd
import sqlite3
from fastapi.responses import StreamingResponse
import io

class TimedRoute(APIRouter):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            return response

        return custom_route_handler
    
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


sqlite_file_path = "C:/Stefan/temp/safety-incidents-api/main/safety.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_path}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()
router = APIRouter(route_class=TimedRoute)


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
    #vehicles = session.exec(select(Vehicle).offset(offset).limit(limit)).all()
    vehicles = session.exec(select(Vehicle)).all()
    return vehicles


@app.get("/vehicle/{vehicle_rec_id}", response_model=VehiclePublicWithIncident)
def read_vehicle(*, session: Session = Depends(get_session), vehicle_rec_id: int):
    vehicle = session.get(Vehicle, vehicle_rec_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Hero not found")
    return vehicle




# @app.patch("/heroes/{hero_id}", response_model=HeroPublic)
# def update_hero(
#     *, session: Session = Depends(get_session), hero_id: int, hero: HeroUpdate
# ):
#     db_hero = session.get(Hero, hero_id)
#     if not db_hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     hero_data = hero.model_dump(exclude_unset=True)
#     for key, value in hero_data.items():
#         setattr(db_hero, key, value)
#     session.add(db_hero)
#     session.commit()
#     session.refresh(db_hero)
#     return db_hero


# @app.delete("/heroes/{hero_id}")
# def delete_hero(*, session: Session = Depends(get_session), hero_id: int):
#     hero = session.get(Hero, hero_id)
#     if not hero:
#         raise HTTPException(status_code=404, detail="Hero not found")
#     session.delete(hero)
#     session.commit()
#     return {"ok": True}


# @app.post("/teams/", response_model=IncidentPublic)
# def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
#     db_team = Team.model_validate(team)
#     session.add(db_team)
#     session.commit()
#     session.refresh(db_team)
#     return db_team


@app.get("/incidents/", response_model=list[IncidentPublic])
def read_incidents(
    *,
    session: Session = Depends(get_session),
    #offset: int = 0,
    #limit: int = Query(default=100, le=100),
):
    incidents = session.exec(select(Incident)).all()
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

# Preferred way  
@app.get("/pandasJSON")
def get_data_pandasJSON():
    con = sqlite3.connect(sqlite_file_path)
    #con = sqlite3.connect("C:/Stefan/safety-incidents-api/main/database.db")
    vehicles = pd.read_sql_query("SELECT * from Vehicle", con)
    #vehicles = vehicles.head(100)
    return Response(vehicles.to_json(orient="records"), media_type="application/json")  

@app.get("/get_csv")
async def get_csv():
    con = sqlite3.connect(sqlite_file_path)
    #con = sqlite3.connect("C:/Stefan/safety-incidents-api/main/database.db")
    vehicles = pd.read_sql_query("SELECT * from Vehicle", con)
    vehicles = vehicles.head(100)
    stream = io.StringIO()
    vehicles.to_csv(stream, index = False)
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv"
                                )
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response


# @app.patch("/teams/{team_id}", response_model=TeamPublic)
# def update_team(
#     *,
#     session: Session = Depends(get_session),
#     team_id: int,
#     team: TeamUpdate,
# ):
#     db_team = session.get(Team, team_id)
#     if not db_team:
#         raise HTTPException(status_code=404, detail="Team not found")
#     team_data = team.model_dump(exclude_unset=True)
#     for key, value in team_data.items():
#         setattr(db_team, key, value)
#     session.add(db_team)
#     session.commit()
#     session.refresh(db_team)
#     return db_team


# @app.delete("/teams/{team_id}")
# def delete_team(*, session: Session = Depends(get_session), team_id: int):
#     team = session.get(Team, team_id)
#     if not team:
#         raise HTTPException(status_code=404, detail="Team not found")
#     session.delete(team)
#     session.commit()
#     return {"ok": True}