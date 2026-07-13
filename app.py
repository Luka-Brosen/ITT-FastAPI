import os
from typing import Optional, List

import pymongo.server_api
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from pydantic.functional_validators import BeforeValidator
from scipy.signal import unique_roots

from typing_extensions import Annotated

from bson import ObjectId
import asyncio
from pymongo import AsyncMongoClient
from pymongo import ReturnDocument


app = FastAPI(
    title="Student Course API",
)
uri = "mongodb+srv://lukabrosen19_db_user:5u3GoX4ZiJnCvWnM@cluster0.ntxgiau.mongodb.net/"
client = AsyncMongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))

db = client.steinam
stunden_collection = db.get_collection("Stundenplan")



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



class StundenplanCollection(BaseModel):
    """
    A container holding a list of `Stundenplan` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    #students: List[StudentModel]
    stundenplan: List[StundenplanModel]



@app.get(
    "/stundenplan/",
    response_description="List all Stundenplan entries",
    response_model=StundenplanCollection,
    response_model_by_alias=False,
)
async def list_stunden():
    return StundenplanCollection(stundenplan=await stunden_collection.find().to_list(1000))



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
