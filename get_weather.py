import logging
import argparse
import urllib.request
import json
from enum import Enum


class DarkSkyApi:
    def __init__(self, key):
        self._key = key

    def key(self, k=None):
        if k:
            self._key = k
        return self._key

    def __str__(self):
        return f'DarSkyAPI key: {self.key()}'


class WeatherLocation:
    def __init__(self, latitude, longitude):
        self._lat = latitude
        self._lon = longitude

    def lat(self, lat=None):
        if lat:
            self._lat = lat
        return self._lat

    def lon(self, lon=None):
        if lon:
            self._lon = lon
        return self._lon

    def __str__(self):
        return f'Weather location: {self.lat()}, {self.lon()}'


class Weather(Enum):
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

    @staticmethod
    def get_from_string(s):
        if s == 'clear-day':
            return Weather.DAY_CLEAR
        elif s == 'clear-night':
            return Weather.NIGHT_CLEAR
        elif s == 'rain':
            return Weather.RAIN
        elif s == 'sleet':
            return Weather.SLEET
        elif s == 'wind':
            return Weather.WIND
        elif s == 'fog':
            return Weather.FOG
        elif s == 'cloudy':
            return Weather.CLOUDY
        elif s == 'partly-cloudy-day':
            return Weather.DAY_PARTLY_CLOUDY
        elif s == 'partly-cloudy-night':
            return Weather.NIGHT_PARTLY_CLOUDY
        return Weather.UNKNOWN


class Temperature:
    def __init__(self, t_cur, t_max, t_min):
        self._cur = t_cur
        self._min = t_min
        self._max = t_max

    def cur(self, t=None):
        if t:
            self._cur = t
        return self._cur

    def min(self, t=None):
        if t:
            self._min = t
        return self._min

    def max(self, t=None):
        if t:
            self._max = t
        return self._max

    def __str__(self):
        return f'T: {self.min()}/{self.cur()}/{self.max()}'


class WeatherReport:
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
                for k, v in mean_weather.items():
                    if v > best_weather_count:
                        best_weather_count = v
                        self._weather = k

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
        url = 'https://api.darksky.net/forecast/' + self._api.key() + '/' + self._location.lat() + ',' + \
              self._location.lon() + '?lang=' + self.lang() + '&units=si&exclude=daily'
        logging.info(f'Contacting DarkSky with following url: {url}')

        with urllib.request.urlopen(url) as request:
            if request.getcode() != 200:
                logging.error(f'Failed to reach DarkSky, error code = {request.getcode()}')
                return False
            data = json.loads(request.read())
            logging.info('Data retrieved from DarkSky')

        self._read_json(data)
        return True

    def __str__(self):
        return f'{self.weather()}, {self.summary()}, {self.temp()}, rain: {int(self.risk_of_rain()*100)}%'


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
