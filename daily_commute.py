import argparse
import logging
import configparser
import os

from get_events import FastMailCalendar
from get_weather import DarkSkyApi, WeatherReport, WeatherLocation
from upload_page import upload_to
import write_page


class ConfigDailyCommute:
    def __init__(self, config_name: str):
        parser = configparser.RawConfigParser()
        parser.read(config_name)
        section = 'TheDailyCommute'
        if not parser.has_section(section):
            raise KeyError(f'Missing "{section}" section in config {config_name}')

        options = ('darksky_key', 'lat', 'lon',
                   'fastmail_usr', 'fastmail_pwd', 'fastmail_url',
                   'ftp_url', 'ftp_usr', 'ftp_pwd', 'ftp_dir')
        values = []
        for option in options:
            # Will raise an exception if option doesn't exist, which is what we want
            v = parser.get(section, option)
            values.append(v)

        self._darsky_key = values[0]
        self._lat = values[1]
        self._lon = values[2]
        self._fastmail_usr = values[3]
        self._fastmail_pwd = values[4]
        self._fastmail_url = values[5]
        self._ftp_url = values[6]
        self._ftp_usr = values[7]
        self._ftp_pwd = values[8]
        self._ftp_dir = values[9]

    def darsky_key(self):
        return self._darsky_key

    def lat(self):
        return self._lat

    def lon(self):
        return self._lon

    def fastmail_usr(self):
        return self._fastmail_usr

    def fastmail_pwd(self):
        return self._fastmail_pwd

    def fastmail_url(self):
        return self._fastmail_url

    def ftp_url(self):
        return self._ftp_url

    def ftp_usr(self):
        return self._ftp_usr

    def ftp_pwd(self):
        return self._ftp_pwd

    def ftp_dir(self):
        return self._ftp_dir


def main():
    logging.getLogger().setLevel(logging.INFO)
    log_format = '(%(asctime)s) [%(levelname)s] %(message)s'
    logging.basicConfig(format=log_format, filename='tdc.log', filemode='a')
    parser = argparse.ArgumentParser(description='Create the Daily Commute')
    parser.add_argument('--config', dest='config', required=True, help='Configuration file for The Daily Commute')
    args = parser.parse_args()

    try:
        daily_config = ConfigDailyCommute(args.config)
    except Exception as e:
        logging.exception(e)
        return 1

    # Weather
    try:
        api = DarkSkyApi(daily_config.darsky_key())
        loc = WeatherLocation(daily_config.lat(), daily_config.lon())
        report = WeatherReport(api, loc)
    except Exception as e:
        logging.exception(e)
        return 1

    if not report.get_report():
        logging.error('Failed to get report')
        return 1

    # Calendar
    try:
        cal = FastMailCalendar(daily_config.fastmail_usr(), daily_config.fastmail_pwd(), daily_config.fastmail_url())
        events = cal.get_today_events()
    except Exception as e:
        logging.exception(e)
        return 1

    # HTML
    write_page.write_html(report, events, 'tdc.html')

    logging.info('The current issue of the Daily Commute is printed')

    # Send to FTP
    if not upload_to(daily_config.ftp_url(), daily_config.ftp_usr(),
                     daily_config.ftp_pwd(), daily_config.ftp_dir(), 'tdc.html'):
        return 1

    # Clean tmp file
    os.remove('tdc.html')

    return 0


if __name__ == '__main__':
    main()
