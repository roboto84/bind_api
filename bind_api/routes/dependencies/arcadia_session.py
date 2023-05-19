
from logging import Logger
from typing import Any
from arcadia.library.arcadia import Arcadia
from datetime import date
from .utils import is_data_stale
import random


class ArcadiaSession:
    _daily_random_tags: dict[str:list[str]] = {}

    def __init__(self, logging: Any, arcadia: Arcadia):
        self._logger: Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._arc = arcadia

    def get_arc(self):
        return self._arc

    def get_random_tags(self) -> dict:
        self._check_random_tags_lifetime()
        return self._daily_random_tags

    def set_new_daily_random_tags(self):
        subjects: list[str] = self._arc.get_subjects()
        if subjects:
            self._daily_random_tags['tags'] = sorted(random.sample(subjects, 35))
            self._daily_random_tags['random_tags_issued_date']: date = date.today()
            return True
        return False

    def _check_random_tags_lifetime(self) -> None:
        self._logger.info('Checking random tags lifetime')
        if 'random_tags_issued_date' in self._daily_random_tags:
            if is_data_stale(self._daily_random_tags['random_tags_issued_date']):
                self.set_new_daily_random_tags()
        else:
            self.set_new_daily_random_tags()
