
from typing import Optional
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from air_core.library.air_db import AirDb
from wh00t_core.library.client_network import ClientNetwork
from .dependencies.dependencies import dependencies

router = APIRouter()


@cbv(router)
class AirApi:
    wh00t_socket: ClientNetwork = Depends(dependencies.get_wh00t_socket)
    air_db: AirDb = Depends(dependencies.get_air_db)
    weather_units: dict = dependencies.get_empty_air().get_units()

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
        weather_history: list[dict] = self.air_db.get_weather_history(history_record_count)
        return {
            'weather_units': self.weather_units,
            'weather_history': weather_history
        }

    @router.get('/air/current_weather', status_code=status.HTTP_200_OK)
    def air_current_weather(self):
        current_weather_data: dict = self.air_db.get_current_weather()
        return {
            'weather_units': self.weather_units,
            'current_weather': current_weather_data
        }

    @router.get('/air/weather_forecast', status_code=status.HTTP_200_OK)
    def air_weather_forecast(self):
        forecast_weather_data: list[dict] = self.air_db.get_weather_forecast()
        return {
            'weather_units': self.weather_units,
            'weather_forecast': forecast_weather_data
        }

    @router.get('/air/weather_report', status_code=status.HTTP_200_OK)
    def air_weather_report(self):
        current_weather_data: dict = self.air_db.get_current_weather()
        forecast_weather_data: list[dict] = self.air_db.get_weather_forecast()
        return {
            'weather_units': self.weather_units,
            'current_weather': current_weather_data,
            'weather_forecast': forecast_weather_data
        }
