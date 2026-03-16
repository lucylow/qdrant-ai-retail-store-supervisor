# app/geospatial/ws_manager.py
import asyncio
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self.lock:
            self.active_connections.setdefault(channel, []).append(websocket)

    async def disconnect(self, channel: str, websocket: WebSocket) -> None:
        async with self.lock:
            if channel in self.active_connections:
                lst = self.active_connections[channel]
                if websocket in lst:
                    lst.remove(websocket)

    async def broadcast(self, channel: str, message: dict) -> None:
        conns = self.active_connections.get(channel, [])
        to_remove: List[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        async with self.lock:
            for ws in to_remove:
                lst = self.active_connections.get(channel, [])
                if ws in lst:
                    lst.remove(ws)


ws_manager = ConnectionManager()
