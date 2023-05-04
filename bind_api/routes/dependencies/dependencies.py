
import os
import logging.config
from typing import Callable, Optional
from logging import Logger
from sqlite3 import DatabaseError

from air_core.library.air import Air
from air_core.library.types.types import Unit
from arcadia.library.arcadia_types import DataViewType
from dotenv import load_dotenv
from wh00t_core.library.client_network import ClientNetwork
from air_core.library.air_db import AirDb
from lexicon.library.lexicon import Lexicon
from arcadia.library.arcadia import Arcadia
from willow_core.library.file_handler import FileHandler

from .air_session import AirSession
from .web_socket_manager import WebSocketManager
from .lexicon_session import LexiconSession
from .arcadia_session import ArcadiaSession


class Dependencies:
    _version: str = 'n/a'

    def __init__(self):
        logging.config.fileConfig(fname=os.path.abspath('bind_api/bin/logging.conf'), disable_existing_loggers=False)
        self._logger: Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        load_dotenv()
        self._environment: dict = {
            'HOST_SERVER_ADDRESS': str(os.getenv('HOST_SERVER_ADDRESS')),
            'WH00T_SERVER_ADDRESS': str(os.getenv('WH00T_SERVER_ADDRESS')),
            'SOCKET_SERVER_PORT': int(os.getenv('SOCKET_SERVER_PORT')),
            'HTTP_SERVER_PORT': int(os.getenv('HTTP_SERVER_PORT')),
            'AIR_DB': str(os.getenv('AIR_DB')),
            'AIR_LOCATION': str(os.getenv('AIR_LOCATION')),
            'LEXI_DB': str(os.getenv('LEXI_DB')),
            'ARCADIA_DB': str(os.getenv('ARCADIA_DB')),
            'MERRIAM_WEBSTER_API_KEY': str(os.getenv('MERRIAM_WEBSTER_API_KEY')),
            'SSL_KEYFILE': str(os.getenv('SSL_KEYFILE', '')),
            'SSL_CERT_FILE': str(os.getenv('SSL_CERT_FILE', ''))
        }

        self._ssl_state: bool = bool(self._environment['SSL_KEYFILE'] and self._environment['SSL_CERT_FILE'])

        self._air_session: AirSession = AirSession(
            self._environment['AIR_LOCATION'],
            Air(Unit.imperial).get_units(),
            self.set_db(self._environment['AIR_DB'], AirDb)
        )
        self._lexicon_session: LexiconSession = LexiconSession(
            logging,
            Lexicon(
                self._environment['MERRIAM_WEBSTER_API_KEY'],
                self._environment['LEXI_DB'],
                logging
            )
        )
        self._arcadia_session: ArcadiaSession = ArcadiaSession(
            logging,
            Arcadia(
                logging,
                self._environment['ARCADIA_DB'],
                DataViewType.RAW
            )
        )
        self._socket_network: ClientNetwork = ClientNetwork(
            self._environment['WH00T_SERVER_ADDRESS'],
            self._environment['SOCKET_SERVER_PORT'],
            'roboto_api',
            'app',
            logging
        )

        try:
            self._socket_network.sock_it()
        except ConnectionRefusedError as e:
            self._logger.info(f'Looks like wh00t services are unavailable:{e}')
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

    def get_logging(self) -> Logger:
        return self._logger

    def get_version(self) -> str:
        return self._version

    def get_ssl_state(self) -> bool:
        return self._ssl_state

    def get_air_session(self) -> AirSession:
        return self._air_session

    def get_lexicon_session(self) -> LexiconSession:
        return self._lexicon_session

    def get_arcadia_session(self) -> ArcadiaSession:
        return self._arcadia_session

    def get_wh00t_socket(self) -> ClientNetwork:
        return self._socket_network

    def get_web_sock_manager(self) -> WebSocketManager:
        return self._web_sock_manager

    def get_server_settings(self) -> tuple:
        return (
            self._environment['HOST_SERVER_ADDRESS'],
            self._environment['HTTP_SERVER_PORT'],
            self._environment['SSL_KEYFILE'],
            self._environment['SSL_CERT_FILE'],
        )


dependencies: Dependencies = Dependencies()
