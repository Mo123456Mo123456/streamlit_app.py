"""Silver — realtime layer: per-user sockets (DMs/notifications) and
per-stream rooms (live chat). In-memory, suitable for a single API node;
swap for Redis pub/sub when scaling horizontally.
"""
import json
from collections import defaultdict

from fastapi import WebSocket


class Manager:
    def __init__(self) -> None:
        self.user_sockets: dict[int, set[WebSocket]] = defaultdict(set)
        self.stream_rooms: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect_user(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self.user_sockets[user_id].add(ws)

    def disconnect_user(self, user_id: int, ws: WebSocket) -> None:
        self.user_sockets[user_id].discard(ws)

    async def connect_stream(self, stream_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self.stream_rooms[stream_id].add(ws)

    def disconnect_stream(self, stream_id: int, ws: WebSocket) -> None:
        self.stream_rooms[stream_id].discard(ws)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        dead = []
        for ws in self.user_sockets.get(user_id, set()):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.user_sockets[user_id].discard(ws)

    async def broadcast_stream(self, stream_id: int, payload: dict) -> None:
        dead = []
        for ws in self.stream_rooms.get(stream_id, set()):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.stream_rooms[stream_id].discard(ws)


manager = Manager()
