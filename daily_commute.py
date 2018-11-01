import argparse
import logging
from get_events import FastMailCalendar
from get_weather import DarkSkyApi, WeatherReport, WeatherLocation
import write_page


def main():
    logging.getLogger().setLevel(logging.INFO)
    log_format = '[%(levelname)s] %(message)s'
    logging.basicConfig(format=log_format)
    parser = argparse.ArgumentParser(description='Create the Daily Commute')
    parser.add_argument('--key', dest='api_key', required=True, help='DarkSky API Key')
    parser.add_argument('--lat', dest='lat', required=True, help='Latitude')
    parser.add_argument('--lon', dest='lon', required=True, help='Longitude')
    parser.add_argument('--usr', dest='usr', required=True, help='User login for Fastmail')
    parser.add_argument('--pwd', dest='pwd', required=True, help='App password for Fastmail')
    parser.add_argument('--url', dest='url', required=True, help='CalDAV discovery URL')
    parser.add_argument('--out', dest='out', required=True, help='HTML file to write')
    args = parser.parse_args()

    # Weather
    try:
        api = DarkSkyApi(args.api_key)
        loc = WeatherLocation(args.lat, args.lon)
        report = WeatherReport(api, loc)
    except Exception as e:
        logging.exception(e)
        return 1

    if not report.get_report():
        logging.error('Failed to get report')
        return 1

    # Calendar
    try:
        cal = FastMailCalendar(args.usr, args.pwd, args.url)
        events = cal.get_today_events()
    except Exception as e:
        logging.exception(e)
        return 1

    # HTML
    write_page.write_html(report, events, args.out)

    logging.info('The current issue of the Daily Commute is printed')

    return 0


if __name__ == '__main__':
    main()
