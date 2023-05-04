
from air_core.library.air_db import AirDb


class AirSession:
    def __init__(self, location: str, units: dict, db: AirDb):
        self._location: str = location
        self._units: dict = units
        self._air_db: AirDb = db

    def get_location(self):
        return self._location

    def get_units(self):
        return self._units

    def get_db(self):
        return self._air_db
