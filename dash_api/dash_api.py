import os
import logging.config
import uvicorn
import ast
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from server import Server
from wh00t_core.library.client_network import ClientNetwork

origins = ['http://127.0.0.1:8080/']
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,
                   allow_methods=['*'], allow_headers=['*'])


@app.get('/', status_code=status.HTTP_200_OK)
def home():
    return {
        'message': socket_network.get_message_history()
    }


@app.get('/air/', status_code=status.HTTP_200_OK)
def air_home():
    return {
        'message': list(filter(lambda key: key['id'] == 'air_bot', socket_network.get_message_history()))
    }


@app.get('/lexicon/', status_code=status.HTTP_200_OK)
def lexicon_home():
    return {
        'message': list(filter(lambda key: key['id'] == 'lexicon_bot', socket_network.get_message_history()))
    }


@app.get('/lexicon/word_search/{search_word}', status_code=status.HTTP_200_OK)
def lexicon_word_search(search_word: str):
    socket_network.send_message('get_word_definition', str({'search_word': search_word}))
    definition_ready = False
    latest_message_unpacked = {}

    while not definition_ready:
        messages = list(filter(lambda key: key['id'] == 'lexicon_bot', socket_network.get_message_history()))
        last_messages_index = len(messages)-1
        if last_messages_index >= 0:
            latest_message = messages[last_messages_index]
            latest_message_unpacked: dict = ast.literal_eval(latest_message['message'])
            if 'word' in latest_message_unpacked and latest_message_unpacked['word'] == search_word:
                definition_ready = True

    return {
        'search_word': search_word,
        'definition': latest_message_unpacked
    }


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('dash_api/bin/logging.conf'), disable_existing_loggers=False)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT = int(os.getenv('SOCKET_SERVER_PORT'))
        HTTP_SERVER_PORT = int(os.getenv('HTTP_SERVER_PORT'))

        socket_network = ClientNetwork(HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT, 'dash_api', 'app', logging)
        config = uvicorn.Config(app, host=HOST_SERVER_ADDRESS, port=HTTP_SERVER_PORT, log_level='info', loop='asyncio')
        server = Server(config=config)

        with server.run_in_thread():
            socket_network.sock_it()
            socket_network.receive()

    except TypeError as type_error:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
