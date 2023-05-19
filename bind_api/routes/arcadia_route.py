
from arcadia.library.db.db_types import UpdateDbItemResponse, AddDbItemResponse, ArcadiaDataType
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_utils.cbv import cbv
from .dependencies.dependencies import dependencies
from .dependencies.arcadia_session import ArcadiaSession
from .models.arcadia_models import ArcadiaUpdateItem, ArcadiaAddItem

router = APIRouter()


@cbv(router)
class ArcadiaApi:
    arcadia_session: ArcadiaSession = Depends(dependencies.get_arcadia_session)

    @router.get('/arcadia/summary', status_code=status.HTTP_200_OK)
    def arcadia_summary(self):
        try:
            subjects: list[str] = self.arcadia_session.get_arc().get_subjects()
            random_subjects: dict = self.arcadia_session.get_random_tags()['tags']
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'number_of_subjects': len(subjects),
                'number_of_URL_records': 3000,
                'random_subject_sample': random_subjects,
                'subjects': subjects,
                'random_record_sample': 2
            }

    @router.get('/arcadia/random_subjects', status_code=status.HTTP_200_OK)
    def arcadia_random_subjects(self):
        try:
            random_subjects: dict = self.arcadia_session.get_random_tags()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'random_subject_sample': random_subjects
            }

    @router.get('/arcadia/subjects_index', status_code=status.HTTP_200_OK)
    def arcadia_subjects(self):
        try:
            subjects: dict[str:list[str]] = self.arcadia_session.get_arc().get_subjects_dictionary()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'subject_index': subjects
            }

    @router.get('/arcadia/word_search/', status_code=status.HTTP_200_OK)
    def arcadia_search(self, term: str):
        try:
            similar_tags: list = self.arcadia_session.get_arc().get_similar_subjects(term)
            search_results: dict = self.arcadia_session.get_arc().get_summary(term)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return {
                'similar_tags': similar_tags,
                'search_results': search_results
            }

    @router.post('/arcadia/create/', status_code=status.HTTP_200_OK)
    def add_item(self, item: ArcadiaAddItem):
        try:
            add_result: AddDbItemResponse = self.arcadia_session.get_arc().add_item(
                {
                    'data_type': ArcadiaDataType.URL,
                    'content': item.data_key,
                    'tags': item.tags
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return add_result

    @router.put('/arcadia/update/', status_code=status.HTTP_200_OK)
    def update_item(self, item: ArcadiaUpdateItem):
        try:
            new_data_key: str = item.new_data_key if item.new_data_key is not None else item.data_key
            update_result: UpdateDbItemResponse = self.arcadia_session.get_arc().update_item(
                item.data_key, new_data_key, item.title, item.tags, item.description, item.image_location
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return update_result

    @router.delete('/arcadia/remove/', status_code=status.HTTP_200_OK)
    def delete_item(self, data_key: str):
        try:
            delete_result: UpdateDbItemResponse = self.arcadia_session.get_arc().delete_item(data_key)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_417_EXPECTATION_FAILED,
                detail={
                    'status': 'ERROR',
                    'error': str(e)
                })
        else:
            return delete_result
