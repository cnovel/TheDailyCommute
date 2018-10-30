import caldav
from requests.auth import HTTPBasicAuth


class Event:
    PERSO = 0
    WORK = 1
    SPORT = 2
    BIRTHDAY = 3

    def __init__(self, t, name, place, t_start, t_end):
        self._type = t
        self._name = name
        self._place = place
        self._t_start = t_start
        self._t_end = t_end

    def type(self, t=None):
        if t:
            self._type = t
        return self._type

    def name(self, t=None):
        if t:
            self._name = t
        return self._name

    def place(self, t=None):
        if t:
            self._place = t
        return self._place

    def time(self, t_s=None, t_e=None):
        if t_s:
            self._t_start = t_s
        if t_e:
            self._t_end = t_e
        return self._t_start, self._t_end


def main():
    # Not working yet
    pass


if __name__ == '__main__':
    main()