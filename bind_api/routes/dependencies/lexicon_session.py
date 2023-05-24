
from logging import Logger
from typing import Any
from datetime import date
from lexicon.library.lexicon import Lexicon
from .utils import is_data_stale


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

    def set_new_word_of_day(self) -> bool:
        self._word_of_day = self._lexi.get_random_word_def()
        if 'word' in self._word_of_day:
            self._word_of_day['word_of_day_issued_date']: date = date.today()
            return True
        return False

    def _check_word_of_day_lifetime(self) -> None:
        self._logger.info('Checking word of the day lifetime')
        if 'word_of_day_issued_date' in self._word_of_day:
            if is_data_stale(self._word_of_day['word_of_day_issued_date']):
                self.set_new_word_of_day()
        else:
            self.set_new_word_of_day()

    def check_word_of_day_removed(self, word: str):
        if self._word_of_day['word'] == word:
            self.set_new_word_of_day()
