"""Module for retrieving the ephemeris for a certain date"""

import json
import datetime


class Ephemeris:
    """Retrieve the ephemeris from a json file"""
    def __init__(self, json_path):
        with open(json_path, 'r') as file:
            self._json = json.load(file)

    @staticmethod
    def id_to_string(month: int) -> str:
        """
        Convert the month id to a string
        :param month: Month between 1 and 12
        :return: month name in english
        """
        months = ['january', 'february', 'march', 'april', 'may',
                  'june', 'july', 'august', 'september', 'october', 'november', 'december']
        return months[month - 1]

    def get_ephemeris_for(self, month: int, day: int) -> list:
        """
        Get the ephemeris for the specified date
        :param month: Month between 1 and 12
        :param day: Day between 1 and 31
        :return: Two-elements list with name string and possibly Saint-e after
        """
        if month < 1 or month > 12:
            raise ValueError(f'Month {month} is invalid, expect a value between 1 and 12')
        if day < 1 or day > 31:
            raise ValueError(f'Day {day} is invalid, expect a value between 1 and 31')
        if day > 30 and month in [4, 6, 9, 11]:
            raise ValueError(f'Day {day} does not exist in month {self.id_to_string(month)}')
        if day > 29 and month == 2:
            raise ValueError(f'Day {day} does not exist in month {self.id_to_string(month)}')

        return self._json[self.id_to_string(month)][day-1]

    def get_today_ephemeris(self):
        """
        Get the current ephemeris
        :return: Two-elements list with name string and possibly Saint-e after
        """
        now = datetime.datetime.now()
        return self.get_ephemeris_for(now.month, now.day)


def main():
    """
    Examples for using ephemeris
    """
    ephemeris = Ephemeris('data\\ephemeris-fr.json')
    print(ephemeris.get_ephemeris_for(3, 18))
    print(ephemeris.get_today_ephemeris())
    try:
        print(ephemeris.get_ephemeris_for(2, 30))
    except ValueError as value_error:
        print(f'ValueError: {value_error}')
    try:
        print(ephemeris.get_ephemeris_for(13, 20))
    except ValueError as value_error:
        print(f'ValueError: {value_error}')


if __name__ == '__main__':
    main()
