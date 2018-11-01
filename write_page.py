import dominate
from dominate import tags
import logging
import datetime
import time
import locale

import get_weather
import get_quote
from ephemeris import Ephemeris
from get_events import Event


def write_head(doc):
    with doc.head:
        tags.link(rel='stylesheet', href='style.css')


def write_date(doc):
    now = datetime.datetime.now()
    locale.setlocale(locale.LC_ALL, 'fr-FR')
    doc.add(tags.h2(str(time.strftime('%A %d %B %Y', now.timetuple())).capitalize()))


def write_ephemeris(doc):
    ephemeris = Ephemeris('data\\ephemeris-fr.json')
    t = ephemeris.get_today_ephemeris()
    s = t[1] + ' ' + t[0] if t[1] else t[0]
    doc.add(tags.h3(s))


def write_quote(quote):
    tags.p('« ' + quote.text() + ' »', cls='quote')
    tags.p('— ' + quote.author(), cls='author')


def write_qotd(doc):
    with doc:
        with tags.div(cls='qotd'):
            quote = get_quote.get_quote_of_the_day()
            write_quote(quote)


def write_ron_quote(doc):
    with doc:
        with tags.div(cls='ron'):
            quote = get_quote.get_ron_swanson_quote()
            write_quote(quote)


def get_svg_path(weather):
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


def get_temp_svg(temp):
    if temp.max() < 5:
        return 'Icons/Thermometer-Zero.svg'
    if temp.max() < 10:
        return 'Icons/Thermometer-25.svg'
    if temp.max() < 20:
        return 'Icons/Thermometer-50.svg'
    if temp.max() < 30:
        return 'Icons/Thermometer-75.svg'
    return 'Icons/Thermometer-100.svg'


def get_temp_str(temp):
    return f'Il fait {temp.cur()}°C, oscillant entre {temp.min()}°C et {temp.max()}°C'


def get_rain_str(risk_of_rain):
    if risk_of_rain < 0.33:
        return f'Risque de pluie : {int(100*risk_of_rain)}%.'
    if risk_of_rain < 0.66:
        return f'Risque de pluie : {int(100*risk_of_rain)}%, prenez un parapluie'
    return f'Risque de pluie : {int(100*risk_of_rain)}%, prenez un parapluie et un k-way !'


def get_rain_svg(risk_of_rain):
    if risk_of_rain < 0.33:
        return 'Icons/Shades.svg'
    return 'Icons/Umbrella.svg'


def write_weather(doc, report):
    with doc:
        with tags.div(cls='weather'):
            tags.img(src=get_svg_path(report.weather()), alt='Weather icon', cls='icon')
            tags.p(report.summary(), cls='summary')
            tags.img(src=get_temp_svg(report.temp()), alt='Thermometer', cls='icon')
            tags.p(get_temp_str(report.temp()), cls='summary')
            tags.img(src=get_rain_svg(report.risk_of_rain()), alt='Rain', cls='icon')
            tags.p(get_rain_str(report.risk_of_rain()), cls='summary')


def event_type_to_string(event):
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
    with tags.div(cls=event_type_to_string(event)):
        name, location, t = event.get_display_strings()
        tags.p(name, cls='event-name')
        if t:
            tags.p(t, cls='time')
        if location:
            tags.p(location, cls='place')


def write_events(doc, events):
    with doc:
        with tags.div(cls='agenda'):
            tags.img(src='Icons/Calendar.svg', alt='Calendar icon', cls='icon')
            for event in events:
                write_event(event)


def write_body(doc, report, events):
    doc.add(tags.h1('The Daily Commute'))
    write_date(doc)
    write_ephemeris(doc)
    write_qotd(doc)
    write_weather(doc, report)
    write_events(doc, events)
    write_ron_quote(doc)


def write_html(report, events, out):
    logging.info('Creating HTML document')
    doc = dominate.document(title='The Daily Commute')
    write_head(doc)
    write_body(doc, report, events)
    logging.info('Writing HTML document')
    with open(out, 'w') as f:
        f.write(doc.render())
