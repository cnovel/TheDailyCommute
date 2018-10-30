import wikiquote
import urllib.request
import logging
import json


class Quote:
    def __init__(self, t, a):
        self._quote = t
        self._author = a

    def text(self, t=None):
        if t:
            self._quote = t
        return self._quote

    def author(self, a=None):
        if a:
            self._author = a
        return self._author

    def __str__(self):
        return f'{self.text()} - {self.author()}'


def get_quote_of_the_day(lang='fr'):
    t = wikiquote.quote_of_the_day(lang)
    return Quote(t[0], t[1])


def get_ron_swanson_quote():
    url = 'https://ron-swanson-quotes.herokuapp.com/v2/quotes'
    with urllib.request.urlopen(url) as request:
        if request.getcode() != 200:
            logging.error(f'Failed to reach DarkSky, error code = {request.getcode()}')
            return ''
        data = json.loads(request.read())
        return data[0]


def main():
    print(get_quote_of_the_day())
    print(get_ron_swanson_quote())


if __name__ == '__main__':
    main()
