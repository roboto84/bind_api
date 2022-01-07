
import os
import logging.config
from typing import Callable, Optional
from logging import Logger
from threading import Thread
from sqlite3 import DatabaseError
from dotenv import load_dotenv
from wh00t_core.library.client_network import ClientNetwork
from air_core.library.air_db import AirDb
from lexicon.library.lexicon import Lexicon
from willow_core.library.file_handler import FileHandler
from .web_socket_manager import WebSocketManager


class Dependencies:
    _version: str = 'n/a'

    def __init__(self):
        logging.config.fileConfig(fname=os.path.abspath('roboto_api/bin/logging.conf'), disable_existing_loggers=False)
        self._logger: Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        load_dotenv()
        self._environment: dict = {
            'HOST_SERVER_ADDRESS': str(os.getenv('HOST_SERVER_ADDRESS')),
            'SOCKET_SERVER_PORT': int(os.getenv('SOCKET_SERVER_PORT')),
            'HTTP_SERVER_PORT': int(os.getenv('HTTP_SERVER_PORT')),
            'AIR_DB': str(os.getenv('AIR_DB')),
            'LEXI_DB': str(os.getenv('LEXI_DB')),
            'MERRIAM_WEBSTER_API_KEY': str(os.getenv('MERRIAM_WEBSTER_API_KEY')),
            'OXFORD_APP_ID': str(os.getenv('OXFORD_APP_ID')),
            'OXFORD_APP_KEY': str(os.getenv('OXFORD_APP_KEY'))
        }

        self._air_db: AirDb = self.set_db(self._environment['AIR_DB'], AirDb)
        self._lexi: Lexicon = Lexicon(
            self._environment['MERRIAM_WEBSTER_API_KEY'],
            self._environment['OXFORD_APP_ID'],
            self._environment['OXFORD_APP_KEY'],
            self._environment['LEXI_DB'],
            logging
        )
        self._socket_network: ClientNetwork = ClientNetwork(
            self._environment['HOST_SERVER_ADDRESS'],
            self._environment['SOCKET_SERVER_PORT'],
            'roboto_api',
            'app',
            logging
        )
        accept_thread: Thread = Thread(target=self._socket_network.sock_it())
        accept_thread.start()
        accept_thread.join()
        self._web_sock_manager = WebSocketManager(self._socket_network)

    def set_version(self, version) -> None:
        self._version = version

    @staticmethod
    def set_db(env_db_path: str, db_class: Callable) -> Optional[AirDb]:
        if FileHandler.file_exists(env_db_path):
            sqlite_db = db_class(logging, env_db_path)
            return sqlite_db
        else:
            raise DatabaseError('Air_DB SQLite file does not exist')

    def get_version(self) -> str:
        return self._version

    def get_air_db(self) -> AirDb:
        return self._air_db

    def get_lexi(self) -> Lexicon:
        return self._lexi

    def get_wh00t_socket(self) -> ClientNetwork:
        return self._socket_network

    def get_web_sock_manager(self) -> WebSocketManager:
        return self._web_sock_manager

    def get_environment(self) -> dict:
        return self._environment

    def get_logging(self) -> Logger:
        return self._logger


dash_dependencies: Dependencies = Dependencies()
