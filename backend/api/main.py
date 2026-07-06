from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_FILE = (
    ROOT_DIR /
    "data" /
    "scored" /
    "properties_scored.json"
)

@app.get("/properties")
def get_properties():

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)