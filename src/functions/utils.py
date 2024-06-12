from datetime import datetime, timedelta
from .data_handler import read_json
import pytz


def get_datetime(city="America/Vancouver", delta=0, time_str=None):
    """Gets the current time of the city and returns it in date format"""
    tz = pytz.timezone(city)  # Getting the timezone for the city
    city_time = datetime.now(tz) + timedelta(days=delta)  # Getting the time in the city's timezone

    if time_str:
        city_time = city_time.replace(hour=time_str, minute=0, second=0)

    return city_time.strftime("%Y-%m-%d %H:%M:%S")


def needs_update(notify=False):
    """Determines whether to update the pairs data or to send the email based on the input parameter"""
    if notify:
        now = get_datetime()
        next_update = read_json("next_email")["next_email"]
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_update = read_json("next_update")["next_update"]

    if now > next_update:
        return True
    return False
