
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_utils.cbv import cbv
from lexicon.library.lexicon import Lexicon
from .dependencies.dependencies import dependencies
from .dependencies.session import Session
from wh00t_core.library.client_network import ClientNetwork

router = APIRouter()


@cbv(router)
class LexiconApi:
    wh00t_socket: ClientNetwork = Depends(dependencies.get_wh00t_socket)
    lexi: Lexicon = Depends(dependencies.get_lexi)
    session: Session = Depends(dependencies.get_session)

    @router.get('/lexicon/wh00t_messages', status_code=status.HTTP_200_OK)
    def lexicon_wh00t_messages(self):
        try:
            lexicon_messages: list = list(
                filter(lambda key: key['id'] == 'lexicon_bot', self.wh00t_socket.get_message_history())
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'message': lexicon_messages
            }

    @router.get('/lexicon/random_word', status_code=status.HTTP_200_OK)
    def lexicon_random_word(self):
        try:
            random_word_definition: dict = self.lexi.get_random_word_def()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return random_word_definition

    @router.get('/lexicon/word_of_day', status_code=status.HTTP_200_OK)
    def lexicon_get_word_of_day(self):
        try:
            word_of_day: dict = self.session.get_word_of_day()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return word_of_day

    @router.put('/lexicon/word_of_day', status_code=status.HTTP_200_OK)
    def lexicon_gen_word_of_day(self):
        try:
            self.session.set_word_of_day(self.lexi.get_random_word_def())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })

    @router.get('/lexicon/words', status_code=status.HTTP_200_OK)
    def lexicon_words(self):
        try:
            lexicon_words: list[str] = self.lexi.get_stored_words()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'lexicon_words': lexicon_words
            }

    @router.get('/lexicon/word_search/{search_word}', status_code=status.HTTP_200_OK)
    def lexicon_word_search(self, search_word: str):
        try:
            searched_word_definition: dict = self.lexi.get_definition(search_word)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return searched_word_definition
