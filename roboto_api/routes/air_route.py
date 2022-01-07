
from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv
from air_core.library.air_db import AirDb
from wh00t_core.library.client_network import ClientNetwork
from .dependencies.dependencies import dash_dependencies

router = APIRouter()


@cbv(router)
class AirApi:
    wh00t_socket: ClientNetwork = Depends(dash_dependencies.get_wh00t_socket)
    air_db: AirDb = Depends(dash_dependencies.get_air_db)

    @router.get('/air/wh00t_messages', status_code=status.HTTP_200_OK)
    def air_wh00t_messages(self):
        return {
            'message': list(
                filter(lambda key: key['id'] == 'air_bot', self.wh00t_socket.get_message_history())
            )
        }

    @router.get('/air/weather_history', status_code=status.HTTP_200_OK)
    def air_weather_history(self):
        weather_history: list[dict] = self.air_db.get_weather_history()
        return {
            'weather_history': weather_history
        }

    @router.get('/air/current_weather', status_code=status.HTTP_200_OK)
    def air_current_weather(self):
        current_weather_data: dict = self.air_db.get_current_weather()
        return {
            'current_weather': current_weather_data
        }

    @router.get('/air/weather_forecast', status_code=status.HTTP_200_OK)
    def air_weather_forecast(self):
        forecast_weather_data: list[dict] = self.air_db.get_weather_forecast()
        return {
            'weather_forecast': forecast_weather_data
        }
