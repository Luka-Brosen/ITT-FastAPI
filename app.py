import os
from typing import Optional, List

import pymongo.server_api
from fastapi import FastAPI, Body, HTTPException, status
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from bson import ObjectId
from pymongo import AsyncMongoClient


app = FastAPI(
    title="Student Course API",
)
uri = os.getenv("MONGODB_URI")
#uri = "mongodb+srv://lukabrosen19_db_user:5u3GoX4ZiJnCvWnM@cluster0.ntxgiau.mongodb.net/"
client = AsyncMongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))


@app.on_event("startup")
async def startup():
    await client.admin.command("ping")
    print("MongoDB connected")


db = client.steinam
stunden_collection = db.get_collection("Stundenplan")
tageIndex_collection = db.get_collection("TageIndex")
stundenindex_collection = db.get_collection("StundenIndex")



# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]

class StundenplanModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    day: str = Field(...)
    start: str = Field(...)
    end: str = Field(...)
    color: str = Field(...)
    teacher: str = Field(...)
    subject: str = Field(...)
    room: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True )

class TageIndexModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    Monday: str = Field(...)
    Tuesday: str = Field(...)
    Wednesday: str = Field(...)
    Thursday: str = Field(...)
    Friday: str = Field(...)

class StundenIndexModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    Lesson_1: str = Field(...)
    Lesson_2: str = Field(...)
    Lesson_3: str = Field(...)
    Lesson_4: str = Field(...)
    Lesson_5: str = Field(...)
    Lesson_6: str = Field(...)
    Lesson_7: str = Field(...)
    Lesson_8: str = Field(...)
    Lesson_9: str = Field(...)
    Lesson_10: str = Field(...)
    Lesson_11: str = Field(...)

class StundenIndexCollection(BaseModel):
    StundenIndex: List[StundenIndexModel]

class TageIndexCollection(BaseModel):
    TageIndex: List[TageIndexModel]

class StundenplanCollection(BaseModel):
    """
    A container holding a list of `Stundenplan` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    #students: List[StudentModel]
    stundenplan: List[StundenplanModel]


@app.get("/")
async def health():
    return {"status": "ok"}


@app.get("/mongo-health")
async def mongo_health():
    try:
        await client.admin.command("ping")
        return {"mongodb": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get(
    "/stundenplan/",
    response_description="List all Stundenplan entries",
    response_model=StundenplanCollection,
    response_model_by_alias=False,
)
async def list_stunden():
    return StundenplanCollection(stundenplan=await stunden_collection.find().to_list(1000))

@app.get(
    "/Tageindex/",
    response_description="Get the list of days",
    response_model=TageIndexCollection,
    response_model_by_alias=False,
)

async def show_TageIndex():
    return TageIndexCollection(tageIndex=await tageIndex_collection.find().to_list(1000))



@app.get(
    "/stundenplan/{id}",
    response_description="Get a single day",
    response_model=StundenplanModel,
    response_model_by_alias=False,
)

async def show_stunden(id: str):
    if (
        Stunden := await stunden_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return Stunden
    raise HTTPException(status_code=404, detail=f"Stunden {id} not found")

@app.get(
    "/Stundenindex/{id}",
    response_description="Get the index of each lesson in a day",
    response_model=StundenplanModel,
    response_model_by_alias=False,
)
async def show_Stundenindex(id: str):
    if (
        StundenIndex := await stundenindex_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return StundenIndex
    raise HTTPException(status_code=404, detail=f"Stunden {id} not found")