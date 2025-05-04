from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List

app = FastAPI()

# In-memory storage for messages
messages = []

# Pydantic model for message data
class Message(BaseModel):
    user: str
    content: str

# REST endpoint to get all messages
@app.get("/messages", response_model=List[Message])
def get_messages():
    return messages

# REST endpoint to post a new message
@app.post("/messages", response_model=Message)
def post_message(message: Message):
    messages.append(message)
    return message

# WebSocket manager (same as before)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}
