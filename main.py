from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn

app = FastAPI()

# MongoDB 설정
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.zero_ctrl

class Command(BaseModel):
    time: datetime = Field(default_factory=datetime.now, alias="time")
    arg_string: int
    cmd_string: str
    is_finish: int

class Sengsing(BaseModel):
    time: datetime = Field(default_factory=datetime.now, alias="time")
    is_finish: int
    manual_mode: str
    num1: int
    num2: str

@app.post("/command/")
async def add_command(command: Command):
    if await db.commandTable.find_one({"time": command.time}):
        raise HTTPException(status_code=400, detail="Command already exists")
    command_dict = command.dict(by_alias=True)
    await db.commandTable.insert_one(command_dict)
    return {"message": "Command added successfully"}

@app.post("/sengsing/")
async def add_sengsing(sensing: Sengsing):
    if await db.sensingTable.find_one({"time": sensing.time}):
        raise HTTPException(status_code=400, detail="Sensing already exists")
    sensing_dict = sensing.dict(by_alias=True)
    await db.sensingTable.insert_one(sensing_dict)
    return {"message": "Sensing added successfully"}
