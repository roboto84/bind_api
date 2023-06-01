import uvicorn
from logging import Logger
from fastapi import FastAPI
from __init__ import __version__
from server.server import Server
from routes.dependencies.dependencies import dependencies
from fastapi.middleware.cors import CORSMiddleware
from routes import root_route, air_route, lexicon_route, arcadia_route, wh00t_chat_route

description = """
## About
This project is a REST API for [Bind](https://www.roboto84.dev/pages/projects/). 
The repo for this API is hosted @ [bind_api](https://github.com/roboto84/bind_api).
"""

app: FastAPI = FastAPI(
    title="Bind API",
    description=description,
    version=__version__,
    contact={
        "name": "roboto84",
        "url": "https://www.roboto84.dev",
    },
    license_info={
        "name": "GNU General Public License v3.0",
        "url": "https://github.com/roboto84/bind_api/blob/develop/LICENSE",
    },
    swagger_ui_parameters={
        "syntaxHighlight.theme": "obsidian",
        "requestSnippetsEnabled": True,
        "tryItOutEnabled": True,
    }
)

app.include_router(root_route.router)
app.include_router(wh00t_chat_route.router)
app.include_router(air_route.router)
app.include_router(root_route.router)
app.include_router(lexicon_route.router)
app.include_router(arcadia_route.router)
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
        host_address, host_port, ssl_keyfile, ssl_cert_file = dependencies.get_server_settings()
        if dependencies.get_ssl_state():
            logger.info('Running server with embedded SSL')
            server: Server = Server(config=uvicorn.Config(
                app,
                host=host_address,
                port=host_port,
                log_level='info',
                loop='asyncio',
                ssl_keyfile=ssl_keyfile,
                ssl_certfile=ssl_cert_file
            ))
        else:
            logger.info('Running server without embedded SSL')
            server: Server = Server(config=uvicorn.Config(
                app,
                host=host_address,
                port=host_port,
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
