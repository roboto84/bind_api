
import json
from typing import List
from fastapi import WebSocket
from wh00t_core.library.client_network import ClientNetwork


class WebSocketManager:
    def __init__(self, wh00t_network: ClientNetwork):
        self._wh00t_sock: ClientNetwork = wh00t_network
        self._web_sock_connection: List[WebSocket] = []

    def get_wh00t_history(self) -> List[dict]:
        return self._wh00t_sock.get_message_history()

    @staticmethod
    def create_web_sock_package(package: dict):
        return {
            'username': package['username'],
            'time': package['time'],
            'message': package['message']
        }

    def send_wh00t_message(self, username: str, message: str) -> None:
        return self._wh00t_sock.send_message('chat_message', message, username)

    async def receive_wh00t_message(self, package: dict) -> bool:
        if not package:
            # Lost wh00t socket connection
            return False
        elif package['category'] == 'chat_message':
            await self.broadcast(self.create_web_sock_package(package))
            return True
        else:
            return True

    async def connect(self, web_sock: WebSocket) -> None:
        await web_sock.accept()
        self._web_sock_connection.append(web_sock)

    def disconnect(self, web_sock: WebSocket) -> None:
        self._web_sock_connection.remove(web_sock)

    async def broadcast(self, message: dict) -> None:
        for connection in self._web_sock_connection:
            await self.send_web_sock_message(message, connection)

    @staticmethod
    async def send_web_sock_message(message: dict or list[dict], websocket: WebSocket) -> None:
        await websocket.send_text(json.dumps(message))
