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

@app.get("/commands/")
async def get_commands():
    commands = await db.commandTable.find().to_list(1000)
    return commands

@app.get("/sengsings/")
async def get_sengsings():
    sengsings = await db.sensingTable.find().to_list(1000)
    return sengsings

@app.get("/command/{time}")
async def get_command_by_time(time: datetime):
    command = await db.commandTable.find_one({"time": time})
    if command:
        return command
    else:
        raise HTTPException(status_code=404, detail="Command not found")

@app.get("/sengsing/{time}")
async def get_sengsing_by_time(time: datetime):
    sensing = await db.sensingTable.find_one({"time": time})
    if sensing:
        return sensing
    else:
        raise HTTPException(status_code=404, detail="Sensing not found")
