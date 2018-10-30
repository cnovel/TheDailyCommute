import json
import datetime


class Ephemeris:
    def __init__(self, json_path):
        with open(json_path, 'r') as f:
            self._json = json.load(f)

    @staticmethod
    def id_to_string(month):
        months = ['january', 'february', 'march', 'april', 'may',
                  'june', 'july', 'august', 'september', 'october', 'november', 'december']
        return months[month - 1]

    def get_ephemeris_for(self, month, day):
        if month < 1 or month > 12:
            raise ValueError(f'Month {month} is invalid, expect a value between 1 and 12')
        if day < 1 or day > 31:
            raise ValueError(f'Day {day} is invalid, expect a value between 1 and 31')
        if day > 30 and (month == 4 or month == 6 or month == 9 or month == 1):
            raise ValueError(f'Day {day} does not exist in month {self.id_to_string(month)}')
        if day > 29 and month == 2:
            raise ValueError(f'Day {day} does not exist in month {self.id_to_string(month)}')

        return self._json[self.id_to_string(month)][day-1]

    def get_today_ephemeris(self):
        now = datetime.datetime.now()
        return self.get_ephemeris_for(now.month, now.day)


def main():
    ephemeris = Ephemeris('data\\ephemeris-fr.json')
    print(ephemeris.get_ephemeris_for(3, 18))
    print(ephemeris.get_today_ephemeris())
    try:
        print(ephemeris.get_ephemeris_for(2, 30))
    except ValueError as e:
        print(f'ValueError: {e}')
    try:
        print(ephemeris.get_ephemeris_for(13, 20))
    except ValueError as e:
        print(f'ValueError: {e}')


if __name__ == '__main__':
    main()
