"""Handle DarkSky API and weather related classes"""

import logging
import argparse
import urllib.request
import json
from enum import Enum


class DarkSkyApi:
    """Store the DarkSky API key"""
    def __init__(self, key: str):
        self._key = key

    def key(self, k: str = None) -> str:
        """
        Getter/setter for DarkSky api key
        :param k: key string, optional
        :return: api key
        """
        if k is not None:
            self._key = k
        return self._key

    def __str__(self):
        return f'DarSkyAPI key: {self.key()}'


class WeatherLocation:
    """Store a weather location"""
    def __init__(self, latitude: float, longitude: float):
        self._lat = latitude
        self._lon = longitude

    def lat(self, lat: float = None) -> float:
        """
        Getter/setter for latitude
        :param lat: latitude, optional
        :return: latitude
        """
        if lat is not None:
            self._lat = lat
        return self._lat

    def lon(self, lon: float = None) -> float:
        """
        Getter/setter for longitude
        :param lon: longitude, optional
        :return: longitude
        """
        if lon is not None:
            self._lon = lon
        return self._lon

    def __str__(self):
        return f'Weather location: {self.lat()}, {self.lon()}'


class Weather(Enum):
    """Store weather type"""
    UNKNOWN = 0
    DAY_CLEAR = 1
    DAY_PARTLY_CLOUDY = 2
    NIGHT_CLEAR = 3
    NIGHT_PARTLY_CLOUDY = 4
    RAIN = 5
    SNOW = 6
    SLEET = 7
    WIND = 8
    FOG = 9
    CLOUDY = 10

    _translation = {'clear-day': DAY_CLEAR, 'clear-night': NIGHT_CLEAR, 'rain': RAIN,
                    'sleet': SLEET, 'wind': WIND, 'fog': FOG, 'cloudy': CLOUDY,
                    'partly-cloudy-day': DAY_PARTLY_CLOUDY,
                    'partly-cloudy-night': NIGHT_PARTLY_CLOUDY}

    @staticmethod
    def get_from_string(weather_str: str):
        """
        Get type of weather from DarkSky icon string
        :param weather_str: DarkSky icon string
        :return: type of weather
        """
        if weather_str in Weather._translation:
            return Weather._translation[weather_str]
        return Weather.UNKNOWN


class Temperature:
    """Store temperature info for the day"""
    def __init__(self, t_cur: float, t_max: float, t_min: float):
        self._cur = t_cur
        self._min = t_min
        self._max = t_max

    def cur(self, temp: float = None) -> float:
        """
        Getter/setter for current temperature
        :param temp: Current temperature, optional
        :return: current temperature
        """
        if temp is not None:
            self._cur = temp
        return self._cur

    def min(self, temp: float = None) -> float:
        """
        Getter/setter for minimum temperature
        :param temp: Minimum temperature, optional
        :return: minimum temperature
        """
        if temp is not None:
            self._min = temp
        return self._min

    def max(self, temp: float = None) -> float:
        """
        Getter/setter for maximum temperature
        :param temp: Maximum temperature, optional
        :return: maximum temperature
        """
        if temp is not None:
            self._max = temp
        return self._max

    def __str__(self):
        return f'T: {self.min()}/{self.cur()}/{self.max()}'


class WeatherReport:
    """Fetch and store a weather report for the day"""
    def __init__(self, api, location):
        self._api = api
        self._location = location
        self._language = 'fr'
        self._weather = Weather.UNKNOWN
        self._summary = ''
        self._risk_of_rain = 0.
        self._temp = Temperature(None, None, None)

    def temp(self):
        return self._temp

    def risk_of_rain(self):
        return self._risk_of_rain

    def weather(self):
        return self._weather

    def summary(self):
        return self._summary

    def lang(self, lang=None):
        if lang:
            self._language = lang
        return self._language

    def _read_json(self, data):
        # Get the average of the day
        logging.info('Processing hourly data')
        if 'hourly' in data:
            # If available, get the summary of the day
            if 'summary' in data['hourly']:
                self._summary = data['hourly']['summary']
            # Then average some info on the next 8 hours
            if 'data' in data['hourly']:
                self._risk_of_rain = 0
                mean_weather = {}
                hours_span = 8
                for i in range(hours_span):
                    hour = data['hourly']['data'][i]
                    temp = hour['temperature']
                    if self._temp.min() is None or temp < self._temp.min():
                        self._temp.min(temp)
                    if self._temp.max() is None or temp > self._temp.max():
                        self._temp.max(temp)
                    self._risk_of_rain += hour['precipProbability']
                    weather = Weather.get_from_string(hour['icon'])
                    if weather in mean_weather:
                        mean_weather[weather] += 1
                    else:
                        mean_weather[weather] = 1
                self._risk_of_rain /= hours_span

                # Find the average weather of the day
                best_weather_count = 0
                for key, value in mean_weather.items():
                    if value > best_weather_count:
                        best_weather_count = value
                        self._weather = key

        # Get current info for completion
        logging.info('Processing currently data')
        if 'currently' in data:
            if 'temperature' in data['currently']:
                self._temp.cur(data['currently']['temperature'])
            if self._weather == Weather.UNKNOWN and 'icon' in data['currently']:
                self._weather = Weather.get_from_string(data['currently']['icon'])

        # Round temperature
        logging.info('Processing temperature')
        self.temp().cur(int(self.temp().cur()))
        self.temp().min(int(self.temp().min()))
        self.temp().max(int(self.temp().max()))

    def get_report(self):
        url = 'https://api.darksky.net/forecast/' + self._api.key() + '/' + \
              self._location.lat() + ',' + self._location.lon() + \
              '?lang=' + self.lang() + '&units=si&exclude=daily'
        logging.info(f'Contacting DarkSky...')

        with urllib.request.urlopen(url) as request:
            if request.getcode() != 200:
                logging.error(f'Failed to reach DarkSky, error code = {request.getcode()}')
                return False
            data = json.loads(request.read())
            logging.info('Data retrieved from DarkSky')

        self._read_json(data)
        return True

    def __str__(self):
        return f'{self.weather()}, {self.summary()}, {self.temp()},' \
               f' rain: {int(self.risk_of_rain()*100)}%'


def main():
    logging.getLogger().setLevel(logging.INFO)
    log_format = '[%(levelname)s] %(message)s'
    logging.basicConfig(format=log_format)
    parser = argparse.ArgumentParser(description='Get weather information from DarkSky API')
    parser.add_argument('-k', '--key', dest='key', required=True, help='DarkSky API key')
    parser.add_argument('--lat', dest='lat', required=True, help='Latitude')
    parser.add_argument('--lon', dest='lon', required=True, help='Longitude')
    args = parser.parse_args()
    api = DarkSkyApi(args.key)
    location = WeatherLocation(args.lat, args.lon)
    report = WeatherReport(api, location)
    if report.get_report():
        print(report)


if __name__ == '__main__':
    main()
