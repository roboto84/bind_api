
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
        try:
            self._logger.info('Attempting to get word of day')
            self._word_of_day = self._lexi.get_random_word_def()
            if 'word' in self._word_of_day:
                self._logger.info(f'Received word of the day {self._word_of_day["word"]}')
                self._word_of_day['word_of_day_issued_date']: date = date.today()
                return True
            self._logger.info('No word of day received, setting word to empty')
            self._word_of_day = {}
            return False
        except Exception as e:
            self._logger.error(f'Exception was thrown: {str(e)}')

    def _check_word_of_day_lifetime(self) -> None:
        try:
            self._logger.info('Checking word of the day lifetime')
            self._logger.info(self._word_of_day)
            if self._word_of_day and 'word_of_day_issued_date' in self._word_of_day:
                self._logger.info('Checking if word of the day is stale')
                if is_data_stale(self._word_of_day['word_of_day_issued_date']):
                    self._logger.info('Attempting to set new word, due to being stale')
                    self.set_new_word_of_day()
            else:
                self._logger.info('Set new word, due to being empty')
                self.set_new_word_of_day()
        except Exception as e:
            self._logger.error(f'Exception was thrown on: {str(e)}')

    def check_word_of_day_removed(self, word: str):
        try:
            if self._word_of_day['word'] == word:
                self.set_new_word_of_day()
        except Exception as e:
            self._logger.error(f'Exception was thrown: {str(e)}')
