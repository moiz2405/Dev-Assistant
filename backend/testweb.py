import asyncio
import websockets
import json

async def send_message():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = {
            "type": "log",
            "message": "Test log message"
        }
        await websocket.send(json.dumps(message))

asyncio.get_event_loop().run_until_complete(send_message())
