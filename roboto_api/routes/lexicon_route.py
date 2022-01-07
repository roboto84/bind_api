
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from lexicon.library.lexicon import Lexicon
from .dependencies.dependencies import dash_dependencies
from wh00t_core.library.client_network import ClientNetwork

router = APIRouter()


@cbv(router)
class LexiconApi:
    wh00t_socket: ClientNetwork = Depends(dash_dependencies.get_wh00t_socket)
    lexi: Lexicon = Depends(dash_dependencies.get_lexi)

    @router.get('/lexicon/wh00t_messages', status_code=status.HTTP_200_OK)
    def lexicon_wh00t_messages(self):
        return {
            'message': list(
                filter(lambda key: key['id'] == 'lexicon_bot', self.wh00t_socket.get_message_history())
            )
        }

    @router.get('/lexicon/words', status_code=status.HTTP_200_OK)
    def lexicon_words(self):
        lexicon_words: list[str] = self.lexi.get_stored_words()
        return {
            'lexicon_words': lexicon_words
        }

    @router.get('/lexicon/word_search/{search_word}', status_code=status.HTTP_200_OK)
    def lexicon_word_search(self, search_word: str):
        return_object = self.lexi.get_definition(search_word)
        return return_object
