
from logging import Logger
from typing import Any
from arcadia.library.arcadia import Arcadia


class ArcadiaSession:
    def __init__(self, logging: Any, arcadia: Arcadia):
        self._logger: Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._arc = arcadia

    def get_arc(self):
        return self._arc
