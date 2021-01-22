import os
import logging.config
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from server import Server
from client_network import ClientNetwork

app = FastAPI()


@app.get("/")
def home():
    messages = socket_network.get_message_history()
    return {'message': messages}


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('dash_api/bin/logging.conf'), disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT = int(os.getenv('SOCKET_SERVER_PORT'))
        HTTP_SERVER_PORT = int(os.getenv('HTTP_SERVER_PORT'))

        socket_network = ClientNetwork(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT)
        config = uvicorn.Config(app, host=HOST_SERVER_ADDRESS, port=HTTP_SERVER_PORT, log_level='info', loop='asyncio')
        server = Server(config=config)

        with server.run_in_thread():
            socket_network.sock_it()
            socket_network.receive()

    except TypeError as type_error:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
