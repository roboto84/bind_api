import random
from logging import Logger
from typing import Any
from arcadia.library.arcadia import Arcadia
from datetime import date
from arcadia.library.db.db_types import ArcadiaDbRecord
from .utils import is_data_stale


class ArcadiaSession:
    _daily_random_tags: dict[str:list[str]] = {}
    _daily_random_item: dict = {}

    def __init__(self, logging: Any, arcadia: Arcadia):
        self._logger: Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._arc = arcadia

    def get_arc(self):
        return self._arc

    def get_random_daily_tags(self) -> dict:
        self._check_random_daily_tags_lifetime()
        return self._daily_random_tags

    def get_daily_random_item(self) -> dict:
        self._check_random_daily_item_lifetime()
        return self._daily_random_item

    def set_new_daily_random_tags(self) -> bool:
        self._logger.info('Get subject tags')
        subjects: list[str] = self._arc.get_subjects()
        self._daily_random_tags['random_tags_issued_date']: date = date.today()

        if subjects:
            self._logger.info('Structure new daily random tags')
            self._daily_random_tags['tags'] = sorted(random.sample(subjects, 35))
            self._logger.info(self._daily_random_tags)
            return True
        self._logger.info('No tags, so setting tags to empty')
        self._daily_random_tags['tags'] = []
        return False

    def set_new_daily_random_item(self) -> bool:
        self._logger.info('Getting random item')
        item: ArcadiaDbRecord = self._arc.get_random_url_item()

        if item:
            self._logger.info('Random item found, Structuring item')
            self._daily_random_item = item
            self._daily_random_item['random_item_issued_date']: date = date.today()
            return True
        self._logger.info('Random item not found, Setting empty item')
        self._logger.info(self._daily_random_item)
        return False

    def _check_random_daily_tags_lifetime(self) -> None:
        self._logger.info('Checking random daily tags lifetime')
        if 'random_tags_issued_date' in self._daily_random_tags:
            if is_data_stale(self._daily_random_tags['random_tags_issued_date']):
                self.set_new_daily_random_tags()
        else:
            self.set_new_daily_random_tags()

    def _check_random_daily_item_lifetime(self) -> None:
        self._logger.info('Checking random daily item lifetime')
        if 'random_item_issued_date' in self._daily_random_item:
            if is_data_stale(self._daily_random_item['random_item_issued_date']):
                self.set_new_daily_random_item()
        else:
            self.set_new_daily_random_item()

    def check_random_daily_item_removed(self, item_key: str):
        self._logger.info('Checking random daily item did not get removed')
        if 'data' in self._daily_random_item and self._daily_random_item['data'] == item_key:
            self._logger.info('Random daily item was removed, setting a new one')
            self.set_new_daily_random_item()

    def check_random_daily_item_updated(self, item_key: str, new_data_key: str):
        self._logger.info('Checking random daily item did not get updated')
        if 'data' in self._daily_random_item and self._daily_random_item['data'] == item_key:
            self._logger.info('Random daily item was updated, refreshing item data')
            current_lifetime_start = self._daily_random_item['random_item_issued_date']
            item:  ArcadiaDbRecord = self._arc.get_item(new_data_key)
            if item:
                self._daily_random_item = item
                self._daily_random_item['random_item_issued_date']: date = current_lifetime_start
