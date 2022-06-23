
from typing import Optional
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from wh00t_core.library.client_network import ClientNetwork

from .dependencies.air_session import AirSession
from .dependencies.dependencies import dependencies

router = APIRouter()


@cbv(router)
class AirApi:
    wh00t_socket: ClientNetwork = Depends(dependencies.get_wh00t_socket)
    air_session: AirSession = Depends(dependencies.get_air_session)

    @router.get('/air/wh00t_messages', status_code=status.HTTP_200_OK)
    def air_wh00t_messages(self):
        return {
            'message': list(
                filter(lambda key: key['id'] == 'air_bot', self.wh00t_socket.get_message_history())
            )
        }

    @router.get('/air/weather_history', status_code=status.HTTP_200_OK)
    def air_weather_history(self, record_count: Optional[int] = None):
        two_week_hourly_history: int = 168
        history_record_count: int = record_count if record_count else two_week_hourly_history
        return {
            'weather_location': self.air_session.get_location(),
            'weather_units': self.air_session.get_units(),
            'weather_history': self.air_session.get_db().get_weather_history(history_record_count)
        }

    @router.get('/air/current_weather', status_code=status.HTTP_200_OK)
    def air_current_weather(self):
        return {
            'weather_location': self.air_session.get_location(),
            'weather_units': self.air_session.get_units(),
            'current_weather': self.air_session.get_db().get_current_weather()
        }

    @router.get('/air/weather_forecast', status_code=status.HTTP_200_OK)
    def air_weather_forecast(self):
        return {
            'weather_location': self.air_session.get_location(),
            'weather_units': self.air_session.get_units(),
            'weather_forecast': self.air_session.get_db().get_weather_forecast()
        }

    @router.get('/air/weather_report', status_code=status.HTTP_200_OK)
    def air_weather_report(self):
        return {
            'weather_location': self.air_session.get_location(),
            'weather_units': self.air_session.get_units(),
            'current_weather': self.air_session.get_db().get_current_weather(),
            'weather_forecast': self.air_session.get_db().get_weather_forecast()
        }
