
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from .dependencies.dependencies import dependencies
from wh00t_core.library.client_network import ClientNetwork

router = APIRouter()


@cbv(router)
class RootApi:
    wh00t_socket: ClientNetwork = Depends(dependencies.get_wh00t_socket)
    version: str = Depends(dependencies.get_version)

    @router.get('/', status_code=status.HTTP_200_OK)
    def root_home(self):
        return {
            'message': list(reversed(self.wh00t_socket.get_message_history()))
        }

    @router.get('/version/', status_code=status.HTTP_200_OK)
    def version_home(self):
        return {
            'version': self.version
        }

