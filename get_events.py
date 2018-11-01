import caldav
from requests.auth import HTTPBasicAuth
import datetime
import dateutil
import locale
import logging
import argparse


class Event:
    PERSO = 0
    WORK = 1
    SPORT = 2
    BIRTHDAY = 3
    HOLIDAY = 4

    def __init__(self, data: str, type_):
        details = data.split('\n')
        self._summary = None
        self._location = None
        self._utc_start = None
        self._utc_end = None
        self._local_start = None
        self._local_end = None
        self._tz_id = None
        self._date_start = None
        self._date_end = None
        self._all_day = False
        self._type = type_

        for detail in details:
            if detail.startswith('SUMMARY:'):
                self._summary = detail[8:]
            if detail.startswith('LOCATION:'):
                self._location = detail[9:]
            if detail.startswith('DTSTART;'):
                t = detail[8:].split(':')
                assert len(t) == 2
                if t[0].startswith('VALUE=DATE'):
                    self._all_day = True
                    self._date_start = t[1]
                else:
                    self._tz_id = t[0][5:]
                    self._local_start = t[1]
            if detail.startswith('DTEND;'):
                t = detail[6:].split(':')
                assert len(t) == 2
                if t[0].startswith('VALUE=DATE'):
                    self._date_end = t[1]
                else:
                    self._local_end = t[1]
            if detail.startswith('DTSTART:') and not detail.startswith('19700101'):
                self._utc_start = detail[8:]
            if detail.startswith('DTEND:'):
                self._utc_end = detail[6:]

        self._process_times()

    def _process_times(self):
        if self._local_start is not None:
            self._local_start = datetime.datetime.strptime(self._local_start, '%Y%m%dT%H%M%S')
        if self._local_end is not None:
            self._local_end = datetime.datetime.strptime(self._local_end, '%Y%m%dT%H%M%S')
        if self._utc_start is not None:
            format_string = '%Y%m%dT%H%M%S'
            if self._utc_start.endswith('Z'):
                format_string += 'Z'
            self._utc_start = datetime.datetime.strptime(self._utc_start, format_string)
        if self._utc_end is not None:
            format_string = '%Y%m%dT%H%M%S'
            if self._utc_end.endswith('Z'):
                format_string += 'Z'
            self._utc_end = datetime.datetime.strptime(self._utc_end, format_string)
        if self._date_start is not None:
            self._date_start = datetime.datetime.strptime(self._date_start, '%Y%m%d')
        if self._date_end is not None:
            self._date_end = datetime.datetime.strptime(self._date_end, '%Y%m%d')

        if not self.is_all_day_event():
            self._get_utc_times()

    def _get_utc_times(self):
        if self._utc_start is not None and self._utc_end is not None:
            return None
        from_zone = dateutil.tz.gettz(self._tz_id)
        to_zone = dateutil.tz.tzutc()
        start = self._local_start
        end = self._local_end
        start = start.replace(tzinfo=from_zone)
        end = end.replace(tzinfo=from_zone)
        self._utc_start = start.astimezone(to_zone)
        self._utc_end = end.astimezone(to_zone)

    def is_all_day_event(self):
        return self._all_day

    def type(self):
        return self._type

    def summary(self):
        if self._summary is not None:
            return self._summary
        return ''

    def location(self):
        if self._location is not None:
            return self._location
        return ''

    def get_start(self):
        if self.is_all_day_event():
            return self._date_start
        return self._utc_start

    def is_happening_today(self):
        now = datetime.datetime.now()
        day_start = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=1)
        day_end = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23, minute=59, second=59)

        if self.is_all_day_event():
            max_start = day_start if day_start > self._date_start else self._date_start
            min_end = day_end if day_end < self._date_end else self._date_end
            return max_start < min_end

        from_zone = dateutil.tz.tzutc()
        to_zone = dateutil.tz.tzlocal()
        day_start = day_start.replace(tzinfo=to_zone)
        day_end = day_end.replace(tzinfo=to_zone)
        utc_start = self._utc_start.replace(tzinfo=from_zone)
        utc_end = self._utc_end.replace(tzinfo=from_zone)
        cur_start = utc_start.astimezone(to_zone)
        cur_end = utc_end.astimezone(to_zone)

        max_start = day_start if day_start > cur_start else cur_start
        min_end = day_end if day_end < cur_end else cur_end
        return max_start < min_end

    def get_display_strings(self):
        if self.is_all_day_event():
            return self.summary(), self.location(), ''

        now = datetime.datetime.now()
        day_start = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=1)
        day_end = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=23, minute=59, second=59)
        from_zone = dateutil.tz.tzutc()
        to_zone = dateutil.tz.tzlocal()
        day_start = day_start.replace(tzinfo=to_zone)
        day_end = day_end.replace(tzinfo=to_zone)
        utc_start = self._utc_start.replace(tzinfo=from_zone)
        utc_end = self._utc_end.replace(tzinfo=from_zone)
        cur_start = utc_start.astimezone(to_zone)
        cur_end = utc_end.astimezone(to_zone)

        locale.setlocale(locale.LC_ALL, 'fr-FR')
        if cur_start < day_start:
            start_info = str(datetime.datetime.strftime(cur_start, '%A %d %B @ %H:%M'))
        else:
            start_info = str(datetime.datetime.strftime(cur_start, '%H:%M'))

        if cur_end > day_end:
            end_info = str(datetime.datetime.strftime(cur_end, '%A %d %B @ %H:%M'))
        else:
            end_info = str(datetime.datetime.strftime(cur_end, '%H:%M'))

        return self.summary(), self.location(), start_info + ' - ' + end_info

    def __lt__(self, other):
        start = self.get_start()
        o_start = other.get_start()
        start = start.replace(tzinfo=dateutil.tz.tzutc())
        o_start = o_start.replace(tzinfo=dateutil.tz.tzutc())
        return start < o_start

    def __repr__(self):
        return f'Event {self.summary()} @ {self.location()}'

    def __str__(self):
        return f'Event {self.summary()} @ {self.location()}'


class FastMailCalendar:
    def __init__(self, username, pwd, discovery_url):
        auth = HTTPBasicAuth(username=username, password=pwd)
        client = caldav.DAVClient(discovery_url, auth=auth)
        self._principal = client.principal()

    def get_today_events(self):
        events = []
        for cal in self._principal.calendars():
            prop = cal.get_properties([caldav.dav.DisplayName()])
            name = prop['{DAV:}displayname']

            if name == 'Agenda':
                t = Event.PERSO
            elif name == 'Work':
                t = Event.WORK
            elif name == 'Jours fériés en France':
                t = Event.HOLIDAY
            elif name == 'Sports':
                t = Event.SPORT
            else:
                continue

            logging.info(f'Processing calendar {name}')
            for event in cal.events():
                e = Event(event.data, t)
                if e.is_happening_today():
                    logging.info(f'{e.summary()} is happening today')
                    events.append(e)
        return sorted(events)


def main():
    logging.getLogger().setLevel(logging.INFO)
    log_format = '[%(levelname)s] %(message)s'
    logging.basicConfig(format=log_format)
    parser = argparse.ArgumentParser(description='Get Fastmail events')
    parser.add_argument('-u', '--user', dest='usr', required=True, help='User login')
    parser.add_argument('-p', '--password', dest='pwd', required=True, help='User password')
    parser.add_argument('--url', dest='url', required=True, help='CalDAV discovery URL')
    args = parser.parse_args()
    my_calendar = FastMailCalendar(username=args.usr, pwd=args.pwd, discovery_url=args.url)

    events = my_calendar.get_today_events()
    for event in events:
        s, l, t = event.get_display_strings()
        print(s, l, t)


if __name__ == '__main__':
    main()
