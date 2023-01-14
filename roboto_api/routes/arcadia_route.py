
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_utils.cbv import cbv
from .dependencies.dependencies import dependencies
from .dependencies.arcadia_session import ArcadiaSession
from wh00t_core.library.client_network import ClientNetwork

router = APIRouter()


@cbv(router)
class ArcadiaApi:
    wh00t_socket: ClientNetwork = Depends(dependencies.get_wh00t_socket)
    arcadia_session: ArcadiaSession = Depends(dependencies.get_arcadia_session)

    @router.get('/arcadia/subjects', status_code=status.HTTP_200_OK)
    def arcadia_subjects(self):
        try:
            subjects: list[str] = self.arcadia_session.get_arc().get_subjects_dictionary()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'arcadia_subjects': subjects
            }

    @router.get('/arcadia/word_search/{search_word}', status_code=status.HTTP_200_OK)
    def arcadia_search(self, search_word: str):
        try:
            search_results: dict = self.arcadia_session.get_arc().get_summary(search_word)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return search_results
