from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uvicorn

app = FastAPI()

# MongoDB 설정
client = AsyncIOMotorClient('mongodb://localhost:27017')
db = client.zero_ctrl

class Move(BaseModel):
    direction: str
    speed: int
    is_finish: int

class ToggleMove(BaseModel):
    mode: str

class Adjustments(BaseModel):
    speed_gain: float
    steering_gain: float
    steering_bias: float

class Gripper(BaseModel):
    action: str

class MoveXY(BaseModel):
    x: int
    y: int

class CameraMove(BaseModel):
    direction: str

class TargetArea(BaseModel):
    color: str

class AGVCommand(BaseModel):
    time: datetime = Field(default_factory=datetime.now, alias="time")
    upload: str
    move: Move
    toggle_move: ToggleMove
    adjustments: Adjustments
    gripper: Gripper
    move_xy: MoveXY
    camera_move: CameraMove
    target_area: TargetArea

def fix_id(obj):
    if "_id" in obj:
        obj["_id"] = str(obj["_id"])
    return obj

@app.post("/agvcommand/")
async def add_agv_command(command: AGVCommand):
    if await db.agvCommandTable.find_one({"time": command.time}):
        raise HTTPException(status_code=400, detail="Command already exists")
    command_dict = command.dict(by_alias=True)
    await db.agvCommandTable.insert_one(command_dict)
    return {"message": "AGV Command added successfully"}

@app.get("/agvcommands/")
async def get_agv_commands():
    commands = await db.agvCommandTable.find().to_list(1000)
    commands = [fix_id(command) for command in commands]
    return commands

@app.get("/agvcommand/{time}")
async def get_agv_command_by_time(time: datetime):
    command = await db.agvCommandTable.find_one({"time": time})
    if command:
        return fix_id(command)
    else:
        raise HTTPException(status_code=404, detail="Command not found")
