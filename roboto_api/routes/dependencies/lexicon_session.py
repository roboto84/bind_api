
from logging import Logger
from typing import Any
from datetime import date
from lexicon.library.lexicon import Lexicon


class LexiconSession:
    _word_of_day: dict = {}

    def __init__(self, logging: Any, lexicon: Lexicon):
        self._logger: Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._lexi = lexicon
        self.set_new_word_of_day()

    def get_lexicon(self):
        return self._lexi

    def get_word_of_day(self) -> dict:
        self._check_word_of_day_lifetime()
        return self._word_of_day

    def set_new_word_of_day(self) -> None:
        self._word_of_day = self._lexi.get_random_word_def()
        self._word_of_day['word_of_day_issued_date']: date = date.today()

    def _check_word_of_day_lifetime(self) -> None:
        self._logger.info('Checking word of the day lifetime')
        if self._is_word_stale(self._word_of_day['word_of_day_issued_date']):
            self.set_new_word_of_day()

    @staticmethod
    def _is_word_stale(stored_date: date) -> bool:
        if date.today().year > stored_date.year:
            return True
        elif date.today().month > stored_date.month:
            return True
        elif date.today().day > stored_date.day:
            return True
        else:
            return False