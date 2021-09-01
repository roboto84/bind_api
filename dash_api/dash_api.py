import os
import logging.config
import uvicorn
import ast
import time
from __init__ import __version__
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


@app.get('/version/', status_code=status.HTTP_200_OK)
def air_home():
    return {
        'version': __version__
    }


@app.get('/air/', status_code=status.HTTP_200_OK)
def air_home():
    return {
        'message': list(filter(lambda key: key['id'] == 'air_bot', socket_network.get_message_history()))
    }


@app.get('/chat/', status_code=status.HTTP_200_OK)
def air_home():
    return {
        'message': list(filter(lambda key: key['profile'] == 'user', socket_network.get_message_history()))
    }


@app.get('/lexicon/', status_code=status.HTTP_200_OK)
def lexicon_home():
    return {
        'message': list(filter(lambda key: key['id'] == 'lexicon_bot', socket_network.get_message_history()))
    }


@app.get('/lexicon/word_search/{search_word}', status_code=status.HTTP_200_OK)
def lexicon_word_search(search_word: str):
    return_object: dict = {
        'search_word': search_word,
        'spelling_suggestions': ['Sorry, even suggestions could not be found.'],
        'definition': {
            'merriam_webster': {
                'state': 'unavailable',
                'word_break': 'unknown',
                'pronounce': 'unknown',
                'date_first_used': 'n/a',
                'etymology': 'unknown',
                'stems': [],
                'definition': ['word was not found.']
            },
            'oxford': {
                'state': 'unavailable',
                'word': search_word,
                'part_of_speech': 'unknown',
                'pronounce': 'unknown',
                'audio': '',
                'definition': [],
                'example': 'none'
            }
        }
    }
    socket_network.send_message('get_word_definition', str({'search_word': search_word}))
    result_ready: bool = False
    max_loops: int = 20
    max_loop_counter: int = 0

    while not result_ready and max_loop_counter < max_loops:
        messages = list(filter(lambda key: key['id'] == 'lexicon_bot', socket_network.get_message_history()))
        for message in messages:
            message_unpacked: dict = ast.literal_eval(message['message'])
            if message_unpacked['search_word'] == search_word:
                if message_unpacked['merriam_webster']['state'] == 'available':
                    return_object['definition']['merriam_webster'] = message_unpacked['merriam_webster']
                if message_unpacked['oxford']['state'] == 'available':
                    return_object['definition']['oxford'] = message_unpacked['oxford']
                if len(message_unpacked['spelling_suggestions']) > 0:
                    return_object['spelling_suggestions'] = message_unpacked['spelling_suggestions']
                result_ready = True
                break
        max_loop_counter += 1
        time.sleep(.25)
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
