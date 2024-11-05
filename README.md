
# Setup

The api runs against a sqlite database that must first be created locally from data in Elmer:
From the root folder of this repo, run `python .\utilities\export_to_sqlite.py`

# Start the API
To run the api (from the ./main folder), execute the following command at the terminal:

`uvicorn incident_api:app --host "0.0.0.0" --port 8000 --reload`

This will host the api at localhost:8000

