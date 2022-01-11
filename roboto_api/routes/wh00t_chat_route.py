
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi_utils.cbv import cbv
from wh00t_core.library.client_network import NetworkUtils
from .dependencies.dependencies import dash_dependencies
from .dependencies.web_socket_manager import WebSocketManager

router = APIRouter()


@cbv(router)
class ChatApi:
    web_sock_manager: WebSocketManager = Depends(dash_dependencies.get_web_sock_manager)

    @router.websocket("/wh00t_chat/{client_id}")
    async def websocket_endpoint(self, websocket: WebSocket, client_id: str):
        await self.web_sock_manager.connect(websocket)

        message_history: list[dict] = list(filter(
            lambda key: key['category'] == 'chat_message', self.web_sock_manager.get_wh00t_history()))
        message_history = [self.web_sock_manager.create_web_sock_package(message) for message in message_history]
        await self.web_sock_manager.send_web_sock_message(message_history, websocket)

        # TODO: Quiet web socket client connection for now until session can be managed better
        # self.web_sock_manager.send_wh00t_message(client_id,
        #                                         f'{client_id} has connected at {NetworkUtils.message_time()}')

        try:
            while True:
                web_sock_message = await websocket.receive_text()
                self.web_sock_manager.send_wh00t_message(client_id, web_sock_message)
        except WebSocketDisconnect:
            self.web_sock_manager.disconnect(websocket)

            # TODO: Quiet web socket client disconnection for now until session can be managed better
            # self.web_sock_manager.send_wh00t_message(client_id,
            #                                         f'{client_id} has left the chat at {NetworkUtils.message_time()}')
