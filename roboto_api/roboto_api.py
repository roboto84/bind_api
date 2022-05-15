
import uvicorn
from logging import Logger
from fastapi import FastAPI
from __init__ import __version__
from server.server import Server
from routes.dependencies.dependencies import dependencies
from fastapi.middleware.cors import CORSMiddleware
from routes import root_route, air_route, lexicon_route, wh00t_chat_route

app: FastAPI = FastAPI()
app.include_router(root_route.router)
app.include_router(wh00t_chat_route.router)
app.include_router(air_route.router)
app.include_router(lexicon_route.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

if __name__ == '__main__':
    logger: Logger = dependencies.get_logging()
    try:
        dependencies.set_version(__version__)
        if dependencies.get_ssl_state():
            logger.info('Running server with embedded SSL')
            server: Server = Server(config=uvicorn.Config(
                app,
                host=dependencies.get_environment()['HOST_SERVER_ADDRESS'],
                port=dependencies.get_environment()['HTTP_SERVER_PORT'],
                log_level='info',
                loop='asyncio',
                ssl_keyfile=dependencies.get_environment()['SSL_KEYFILE'],
                ssl_certfile=dependencies.get_environment()['SSL_CERT_FILE']
            ))
        else:
            logger.info('Running server without embedded SSL')
            server: Server = Server(config=uvicorn.Config(
                app,
                host=dependencies.get_environment()['HOST_SERVER_ADDRESS'],
                port=dependencies.get_environment()['HTTP_SERVER_PORT'],
                log_level='info',
                loop='asyncio'
            ))
        with server.run_in_thread():
            dependencies.get_wh00t_socket().receive(
                dependencies.get_web_sock_manager().receive_wh00t_message
            )

    except Exception as error:
        logger.exception('Received Exception: ', error)
        exit()
