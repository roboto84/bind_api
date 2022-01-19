
class Session:
    _word_of_day: dict = {}

    def get_word_of_day(self) -> dict:
        return self._word_of_day

    def set_word_of_day(self, word_data: dict) -> None:
        self._word_of_day = word_data
