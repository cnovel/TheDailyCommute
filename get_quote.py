import wikiquote
import urllib.request
import logging
import json


class Quote:
    def __init__(self, text: str, author: str):
        """
        Constructor for a quote
        :param text: Text of the quote
        :param author: Author of the quote
        """
        self._quote = text
        self._author = author

    def text(self, text: str = None) -> str:
        """
        Getter/setter for the text of the quote
        :param text: New text for the quote, optional
        :return: text of the quote
        """
        if text:
            self._quote = text
        return self._quote

    def author(self, author: str = None) -> str:
        """
        Getter/setter for the author of the quote
        :param author: New author of the quote, optional
        :return: author name
        """
        if author:
            self._author = author
        return self._author

    def __str__(self):
        return f'{self.text()} - {self.author()}'

    def __bool__(self):
        return len(self.text()) > 0 or len(self.author()) > 0


def get_quote_of_the_day(lang: str = 'fr') -> Quote:
    """
    Get the quote of the day from Wikiquote
    :param lang: Language parameters, can be 'en', 'fr', 'it', 'de' or 'es'
    :return: Quote, can be empty
    """
    try:
        t = wikiquote.quote_of_the_day(lang)
        return Quote(t[0], t[1])
    except wikiquote.qotd.utils.UnsupportedLanguageException as e:
        logging.exception(e)
        return Quote('', '')


def get_ron_swanson_quote() -> Quote:
    """
    Get a quote from Ron Swanson
    :return: Quote, can be empty
    """
    url = 'https://ron-swanson-quotes.herokuapp.com/v2/quotes'
    with urllib.request.urlopen(url) as request:
        if request.getcode() != 200:
            logging.error(f'Failed to reach DarkSky, error code = {request.getcode()}')
            return Quote('', '')
        data = json.loads(request.read())
        return Quote(data[0], 'Ron Swanson')


def main():
    q = get_quote_of_the_day()
    if q:
        print(q)
    else:
        print('Quote of the day unreachable')
    q = get_ron_swanson_quote()
    if q:
        print(q)
    else:
        print('Ron Swanson is unavailable')

    q = Quote('', '')
    if q:
        print(q)
    else:
        print('Quote is empty')


if __name__ == '__main__':
    main()
