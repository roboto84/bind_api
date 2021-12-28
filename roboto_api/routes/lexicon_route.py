
import ast
import time
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from lexicon_core.library.db.lexicon_db import LexiconDb
from .dependencies.dependencies import dash_dependencies
from wh00t_core.library.client_network import ClientNetwork

router = APIRouter()


@cbv(router)
class LexiconApi:
    wh00t_socket: ClientNetwork = Depends(dash_dependencies.get_wh00t_socket)
    lexi_db: LexiconDb = Depends(dash_dependencies.get_lexi_db)

    @router.get('/lexicon/', status_code=status.HTTP_200_OK)
    def lexicon_home(self):
        return {
            'message': list(
                filter(lambda key: key['id'] == 'lexicon_bot', self.wh00t_socket.get_message_history())
            )
        }

    @router.get('/lexicon/words', status_code=status.HTTP_200_OK)
    def lexicon_words(self):
        lexicon_words: list[dict] = self.lexi_db.get_words()
        return {
            'lexicon_words': lexicon_words
        }

    @router.get('/lexicon/word_search/{search_word}', status_code=status.HTTP_200_OK)
    def lexicon_word_search(self, search_word: str):
        return_object: dict = {
            'search_word': search_word,
            'spelling_suggestions': ['Sorry, even suggestions could not be found.'],
            'definition': {
                'merriam_webster': {
                    'state': 'unavailable',
                    'word_break': 'unknown',
                    'pronounce': 'unknown',
                    'date_first_used': 'n/a',
                    'etymology': 'unknown',
                    'stems': [],
                    'definition': ['word was not found.']
                },
                'oxford': {
                    'state': 'unavailable',
                    'word': search_word,
                    'part_of_speech': 'unknown',
                    'pronounce': 'unknown',
                    'audio': '',
                    'definition': [],
                    'example': 'none'
                }
            }
        }
        self.wh00t_socket.send_message('get_word_definition', str({'search_word': search_word}))
        result_ready: bool = False
        max_loops: int = 20
        max_loop_counter: int = 0

        while not result_ready and max_loop_counter < max_loops:
            messages = list(filter(lambda data: data['id'] == 'lexicon_bot' and data['category'] == 'word_definition',
                                   self.wh00t_socket.get_message_history()))
            for message in messages:
                message_unpacked: dict = ast.literal_eval(message['message'])
                if message_unpacked['search_word'] == search_word:
                    if message_unpacked['merriam_webster']['state'] == 'available':
                        return_object['definition']['merriam_webster'] = message_unpacked['merriam_webster']
                    if message_unpacked['oxford']['state'] == 'available':
                        return_object['definition']['oxford'] = message_unpacked['oxford']
                    if len(message_unpacked['spelling_suggestions']) > 0:
                        return_object['spelling_suggestions'] = message_unpacked['spelling_suggestions']
                    result_ready = True
                    break
            max_loop_counter += 1
            time.sleep(.25)
        return return_object
