"""Main module for creating a Daily Commute edition"""

import argparse
import logging
import configparser
import os

from get_events import FastMailCalendar
from get_weather import DarkSkyApi, WeatherReport, WeatherLocation
from upload_page import upload_to
import write_page


class FastmailConfig:
    """Stores the fastmail configuration for accessing calendar"""
    def __init__(self, usr: str, pwd: str, url: str):
        self._usr = usr
        self._pwd = pwd
        self._url = url

    def usr(self) -> str:
        """
        Get Fastmail user name
        :return: username as string
        """
        return self._usr

    def pwd(self) -> str:
        """
        Get Fastmail application password for calendar access
        :return: password
        """
        return self._pwd

    def url(self) -> str:
        """
        Get a calendar full address
        :return: url
        """
        return self._url


class FtpConfig:
    """Store the FTP configuration for uploading the Daily Commute"""
    def __init__(self, url: str, usr: str, pwd: str, directory: str):
        self._url = url
        self._usr = usr
        self._pwd = pwd
        self._dir = directory

    def url(self) -> str:
        """
        Get FTP url
        :return: url
        """
        return self._url

    def usr(self) -> str:
        """
        Get FTP user name
        :return: user name
        """
        return self._usr

    def pwd(self) -> str:
        """
        Get FTP password
        :return: password
        """
        return self._pwd

    def dir(self) -> str:
        """
        Get FTP directory where the Daily Commute is saved
        :return: directory
        """
        return self._dir


class ConfigDailyCommute:
    """Store the whole configuration needed for running the Daily Commute"""
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
            value = parser.get(section, option)
            values.append(value)

        self._darsky_key = values[0]
        self._lat = values[1]
        self._lon = values[2]
        self._fastmail_config = FastmailConfig(values[3], values[4], values[5])
        self._ftp_config = FtpConfig(values[6], values[7], values[8], values[9])

    def darsky_key(self) -> str:
        """
        Return DarkSky API key
        :return: string
        """
        return self._darsky_key

    def lat(self) -> float:
        """
        Get latitude for weather prediction
        :return: latitude
        """
        return self._lat

    def lon(self) -> float:
        """
        Get longitude for weather prediction
        :return: longitude
        """
        return self._lon

    def fastmail_usr(self) -> str:
        """
        Get Fastmail user name
        :return: user name as string
        """
        return self._fastmail_config.usr()

    def fastmail_pwd(self) -> str:
        """
        Get Fastmail app password
        :return: password
        """
        return self._fastmail_config.pwd()

    def fastmail_url(self) -> str:
        """
        Get Fastmail calendar URL
        :return: url as string
        """
        return self._fastmail_config.url()

    def ftp_url(self) -> str:
        """
        Get FTP url
        :return: url
        """
        return self._ftp_config.url()

    def ftp_usr(self) -> str:
        """
        Get FTP username
        :return: username
        """
        return self._ftp_config.usr()

    def ftp_pwd(self) -> str:
        """
        Get FTP password
        :return: password
        """
        return self._ftp_config.pwd()

    def ftp_dir(self) -> str:
        """
        Get FTP directory for saving the HTML file
        :return: directory
        """
        return self._ftp_config.dir()


def main():
    """
    Main function for creating and uploading a Daily Commute edition
    :return: status code 0 or 1
    """
    logging.getLogger().setLevel(logging.INFO)
    log_format = '(%(asctime)s) [%(levelname)s] %(message)s'
    logging.basicConfig(format=log_format, filename='tdc.log', filemode='a')
    parser = argparse.ArgumentParser(description='Create the Daily Commute')
    parser.add_argument('--config', dest='config', required=True,
                        help='Configuration file for The Daily Commute')
    args = parser.parse_args()

    try:
        daily_config = ConfigDailyCommute(args.config)
    except Exception as exc:
        logging.exception(exc)
        return 1

    # Weather
    try:
        api = DarkSkyApi(daily_config.darsky_key())
        loc = WeatherLocation(daily_config.lat(), daily_config.lon())
        report = WeatherReport(api, loc)
    except Exception as exc:
        logging.exception(exc)
        return 1

    if not report.get_report():
        logging.error('Failed to get report')
        return 1

    # Calendar
    try:
        cal = FastMailCalendar(daily_config.fastmail_usr(), daily_config.fastmail_pwd(),
                               daily_config.fastmail_url())
        events = cal.get_today_events()
    except Exception as exc:
        logging.exception(exc)
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
