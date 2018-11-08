"""Write the HTML page for the Daily Commute"""

import logging
import datetime
import time
import locale

import dominate
from dominate import tags

import get_weather
import get_quote
from ephemeris import Ephemeris
from get_events import Event


def write_head(doc: dominate.document):
    """
    Write head for HTML document
    :param doc: Dominate document
    """
    with doc.head:
        tags.link(rel='stylesheet', href='style.css')


def write_date(doc: dominate.document):
    """
    Write date in HTML document
    :param doc: Dominate document
    """
    now = datetime.datetime.now()
    locale.setlocale(locale.LC_ALL, 'fr-FR')
    doc.add(tags.h2(str(time.strftime('%A %d %B %Y', now.timetuple())).capitalize()))


def write_ephemeris(doc: dominate.document):
    """
    Write ephemeris in HTML document
    :param doc: Dominate document
    """
    ephemeris = Ephemeris('data\\ephemeris-fr.json')
    today_eph = ephemeris.get_today_ephemeris()
    string_eph = today_eph[1] + ' ' + today_eph[0] if today_eph[1] else today_eph[0]
    doc.add(tags.h3(string_eph))


def write_quote(quote: get_quote.Quote):
    """
    Write quote, requires an open dominate document
    :param quote: Quote to be written
    """
    tags.p('« ' + quote.text() + ' »', cls='quote')
    tags.p('— ' + quote.author(), cls='author')


def write_qotd(doc: dominate.document):
    """
    Write quote of the day in HTML document
    :param doc:  Dominate document
    """
    with doc:
        with tags.div(cls='qotd'):
            quote = get_quote.get_quote_of_the_day()
            write_quote(quote)


def write_ron_quote(doc: dominate.document):
    """
    Write a Ron Swanson quote in HTML document
    :param doc:  Dominate document
    """
    with doc:
        with tags.div(cls='ron'):
            quote = get_quote.get_ron_swanson_quote()
            write_quote(quote)


def get_svg_path(weather: get_weather.Weather) -> str:
    """
    Get SVG path corresponding to weather type
    :param weather: Weather type
    :return: path to SVG resource
    """
    if weather == get_weather.Weather.DAY_CLEAR:
        return 'Icons/Sun.svg'
    if weather == get_weather.Weather.DAY_PARTLY_CLOUDY:
        return 'Icons/Cloud-Sun.svg'
    if weather == get_weather.Weather.NIGHT_CLEAR:
        return 'Icons/Moon.svg'
    if weather == get_weather.Weather.NIGHT_PARTLY_CLOUDY:
        return 'Icons/Cloud-Moon.svg'
    if weather == get_weather.Weather.CLOUDY:
        return 'Icons/Cloud.svg'
    if weather == get_weather.Weather.FOG:
        return 'Icons/Cloud-Fog.svg'
    if weather == get_weather.Weather.RAIN:
        return 'Icons/Cloud-Rain.svg'
    if weather == get_weather.Weather.SNOW:
        return 'Icons/Cloud-Snow.svg'
    if weather == get_weather.Weather.SLEET:
        return 'Icons/Cloud-Snow.svg'
    if weather == get_weather.Weather.WIND:
        return 'Icons/Wind.svg'
    return 'Icons/Compass.svg'


def get_temp_svg(temp: get_weather.Temperature) -> str:
    """
    Get SVG path corresponding to the temperature
    :param temp: Temperature
    :return: path to SVG resource
    """
    if temp.max() < 5:
        return 'Icons/Thermometer-Zero.svg'
    if temp.max() < 10:
        return 'Icons/Thermometer-25.svg'
    if temp.max() < 20:
        return 'Icons/Thermometer-50.svg'
    if temp.max() < 30:
        return 'Icons/Thermometer-75.svg'
    return 'Icons/Thermometer-100.svg'


def get_temp_str(temp: get_weather.Temperature) -> str:
    """
    Return string in french with temperature info
    :param temp: Temperature
    :return: string
    """
    return f'Il fait {temp.cur()}°C, oscillant entre {temp.min()}°C et {temp.max()}°C'


def get_rain_str(risk_of_rain: float) -> str:
    """
    Return string in french with risk of rain info
    :param risk_of_rain: Risk of rain between 0 and 1
    :return: string
    """
    if risk_of_rain < 0.33:
        return f'Risque de pluie : {int(100*risk_of_rain)}%.'
    if risk_of_rain < 0.66:
        return f'Risque de pluie : {int(100*risk_of_rain)}%, prenez un parapluie'
    return f'Risque de pluie : {int(100*risk_of_rain)}%, prenez un parapluie et un k-way !'


def get_rain_svg(risk_of_rain: float) -> str:
    """
    Get SVG path to risk of rain icon
    :param risk_of_rain: Risk of rain between 0 and 1
    :return: path to SVG resource
    """
    if risk_of_rain < 0.33:
        return 'Icons/Shades.svg'
    return 'Icons/Umbrella.svg'


def write_weather(doc: dominate.document, report: get_weather.WeatherReport):
    """
    Write weather report in HTML document
    :param doc: Dominate document
    :param report: Weather report
    """
    with doc:
        with tags.div(cls='weather'):
            tags.img(src=get_svg_path(report.weather()), alt='Weather icon', cls='icon')
            tags.p(report.summary(), cls='summary')
            tags.img(src=get_temp_svg(report.temp()), alt='Thermometer', cls='icon')
            tags.p(get_temp_str(report.temp()), cls='summary')
            tags.img(src=get_rain_svg(report.risk_of_rain()), alt='Rain', cls='icon')
            tags.p(get_rain_str(report.risk_of_rain()), cls='summary')


def event_type_to_string(event: Event) -> str:
    """
    Convert event type to string
    :param event: Event
    :return: description string
    """
    if event.type() == Event.WORK:
        return 'event-work'
    if event.type() == Event.PERSO:
        return 'event-perso'
    if event.type() == Event.SPORT:
        return 'event-sport'
    if event.type() == Event.BIRTHDAY:
        return 'event-bday'
    if event.type() == Event.HOLIDAY:
        return 'event-holiday'
    return 'event-unknown'


def write_event(event: Event):
    """
    Write event to HTML document
    :param event: Event to be written
    """
    with tags.div(cls=event_type_to_string(event)):
        name, location, hours = event.get_display_strings()
        tags.p(name, cls='event-name')
        if hours:
            tags.p(hours, cls='time')
        if location:
            tags.p(location, cls='place')


def write_events(doc: dominate.document, events):
    """
    Write events to HTML document
    :param doc: Dominate document
    :param events: List of events
    """
    with doc:
        with tags.div(cls='agenda'):
            tags.img(src='Icons/Calendar.svg', alt='Calendar icon', cls='icon')
            for event in events:
                write_event(event)


def write_body(doc: dominate.document, report: get_weather.WeatherReport, events):
    """
    Write the body of the Daily Commute
    :param doc: Dominate document
    :param report: Weather report
    :param events: List of events
    """
    doc.add(tags.h1('The Daily Commute'))
    write_date(doc)
    write_ephemeris(doc)
    write_qotd(doc)
    write_weather(doc, report)
    if events:
        write_events(doc, events)
    write_ron_quote(doc)


def write_html(report: get_weather.WeatherReport, events, out: str):
    """
    Write HTML file containing the Daily Commute
    :param report: Weather report
    :param events: List of events
    :param out: path to html file
    """
    logging.info('Creating HTML document')
    doc = dominate.document(title='The Daily Commute')
    write_head(doc)
    write_body(doc, report, events)
    logging.info('Writing HTML document')
    with open(out, 'w') as file:
        file.write(doc.render())
