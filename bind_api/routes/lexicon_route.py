
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_utils.cbv import cbv
from .dependencies.dependencies import dependencies
from .dependencies.lexicon_session import LexiconSession
from wh00t_core.library.client_network import ClientNetwork

router = APIRouter()


@cbv(router)
class LexiconApi:
    wh00t_socket: ClientNetwork = Depends(dependencies.get_wh00t_socket)
    lexicon_session: LexiconSession = Depends(dependencies.get_lexicon_session)

    @router.get('/lexicon/summary', status_code=status.HTTP_200_OK)
    def lexicon_summary(self):
        try:
            word_of_day: dict = self.lexicon_session.get_word_of_day()
            number_of_words: int = self.lexicon_session.get_lexicon().get_record_count()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'number_of_words': number_of_words,
                'word_of_day': word_of_day
            }

    @router.get('/lexicon/wh00t_messages', status_code=status.HTTP_200_OK)
    def lexicon_wh00t_messages(self):
        return {
            'message': list(
                filter(lambda key: key['id'] == 'lexicon_bot', self.wh00t_socket.get_message_history())
            )
        }

    @router.get('/lexicon/random_word', status_code=status.HTTP_200_OK)
    def lexicon_random_word(self):
        try:
            random_word_definition: dict = self.lexicon_session.get_lexicon().get_random_word_def()
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
            word_of_day: dict = self.lexicon_session.get_word_of_day()
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
            result: bool = self.lexicon_session.set_new_word_of_day()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return result

    @router.get('/lexicon/words/{number_of_words}', status_code=status.HTTP_200_OK)
    def lexicon_words(self, number_of_words: int):
        try:
            lexicon_words: list[str] = self.lexicon_session.get_lexicon().get_stored_words(number_of_words)
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
            searched_word_definition: dict = self.lexicon_session.get_lexicon().get_definition(search_word)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return searched_word_definition

    @router.delete('/lexicon/remove/', status_code=status.HTTP_200_OK)
    def delete_item(self, word: str):
        try:
            lowercase_word = word.lower()
            delete_result = self.lexicon_session.get_lexicon().delete_item(lowercase_word)
            if delete_result['deleted_item']:
                self.lexicon_session.check_word_of_day_removed(lowercase_word)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return delete_result
