from fastapi import Depends, FastAPI, HTTPException, Query, APIRouter, Response, Request
import pandas as pd
import json
#from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select
import sqlite3
from fastapi.responses import StreamingResponse
import io
from typing import List
import pydantic
import weakref
import itertools
import types
import pandera as pa
from pandera.typing import Index, DataFrame, Series

app = FastAPI()
# df = pd.read_csv("file.csv")
sqlite_file_path = "./safety.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_path}"

con = sqlite3.connect(sqlite_file_path)

# vehicles = pd.read_sql_query("SELECT * from Vehicle", con)
# incidents = pd.read_sql_query("SELECT * from Incident", con)


class Incidents(pa.DataFrameModel):
    incident_rec_id: Series[int] = pa.Field()
    Collision_Report_Number: Series[str] = pa.Field()
    incident_date: Series[str] = pa.Field()
    City_Name: Series[str] = pa.Field()
    County_Name: Series[str] = pa.Field()
    Latitude: Series[float] = pa.Field()
    Longitude: Series[float] = pa.Field()

    class Config:
        coerce = True


class Vehicles(pa.DataFrameModel):
    vehicle_rec_id: Series[int] = pa.Field()
    incident_rec_id: Series[int] = pa.Field()
    unit_number: Series[int] = pa.Field()
    Vehicle_Type: Series[str] = pa.Field()
    Collision_Report_Number: Series[str] = pa.Field()
    Vehicle_Make: Series[str] = pa.Field()
    Vehicle_Model: Series[str] = pa.Field()
    Vehicle_Style: Series[str] = pa.Field()

    class Config:
        coerce = True

class Persons(pa.DataFrameModel):
    person_rec_id: Series[int] = pa.Field()
    Collision_Report_Number: Series[str] = pa.Field()
    # Involved_Person_Type: Series[str] = pa.Field()
    Age: Series[str] = pa.Field()
    Involved_Person_Type: Series[str] = pa.Field()
    # Injury_Type: Series[str] = pa.Field()

    class Config:
        coerce = True


vehicles = pd.read_sql_query("SELECT * from Vehicle", con)
try:
    Vehicles.validate(vehicles)
except pa.errors.SchemaError as exc:
    print(exc)

incidents = pd.read_sql_query("SELECT * from Incident", con)
try:
    Incidents.validate(incidents)
except pa.errors.SchemaError as exc:
    print(exc)

persons = pd.read_sql_query("SELECT * from Person", con)
try:
    Persons.validate(persons)
except pa.errors.SchemaError as exc:
    print(exc)


@app.get("/incidents", response_model=DataFrame[Incidents])
def get_incidents(County_Name: str | None = None, City_Name: str | None = None):
    df = incidents.copy()
    if County_Name:
        df = df[df["County_Name"] == County_Name]
    if City_Name:
        df = df[df["City_Name"] == City_Name]
    return Response(df.to_json(orient="records"), media_type="application/json")


@app.get("/vehicles/", response_model=DataFrame[Vehicles])
def get_vehicles_by_id(ids: List[str] | None = Query(None)):
    df = vehicles.copy()
    if ids:
        df = df[df["Collision_Report_Number"].isin(ids)]
        return Response(df.to_json(orient="records"), media_type="application/json")
    else:
        return Response(
            vehicles.to_json(orient="records"), media_type="application/json"
        )
    
@app.get("/persons/")
def get_persons_by_id(ids: List[str] | None = Query(None)):
    if ids:
        dfi = incidents[incidents["Collision_Report_Number"].isin(ids)]
        dfp = persons[persons["Collision_Report_Number"].isin(ids)]
    result = []
    for report_num, incident_group in dfi.groupby("Collision_Report_Number"):
        incident_data = incident_group.iloc[0].to_dict()
        incident_data["persons"] = json.loads(dfp.to_json(orient="records"))
        result.append(incident_data)
    
    return Response(json.dumps(result), media_type="application/json")
