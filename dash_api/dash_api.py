import os
import logging.config
import uvicorn
import ast
import time
from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from server import Server
from wh00t_core.library.client_network import ClientNetwork

app: FastAPI = FastAPI()
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
    definition_ready: bool = False
    message_unpacked: dict = {}
    max_loops: int = 20
    max_loop_counter: int = 0

    while not definition_ready and max_loop_counter < max_loops:
        messages = list(filter(lambda key: key['id'] == 'lexicon_bot', socket_network.get_message_history()))
        for message in messages:
            message_unpacked: dict = ast.literal_eval(message['message'])
            if 'word' in message_unpacked and message_unpacked['word'] == search_word:
                definition_ready = True
                break
        max_loop_counter += 1
        time.sleep(.25)

    return_object: dict = {
        'search_word': search_word,
        'definition': message_unpacked
    }
    if max_loop_counter == max_loops:
        return_object['definition'] = {
            'word': search_word,
            'part_of_speech': 'unknown',
            'pronounce': 'unknown',
            'audio': '',
            'definition': ['word was not found.'],
            'example': 'none'
        }
    return return_object


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('dash_api/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))
        HTTP_SERVER_PORT: int = int(os.getenv('HTTP_SERVER_PORT'))

        socket_network: ClientNetwork = ClientNetwork(HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT,
                                                      'dash_api', 'app', logging)
        config: uvicorn.Config = uvicorn.Config(app, host=HOST_SERVER_ADDRESS, port=HTTP_SERVER_PORT,
                                                log_level='info', loop='asyncio')
        server: Server = Server(config=config)

        with server.run_in_thread():
            socket_network.sock_it()
            socket_network.receive()

    except TypeError as type_error:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
