from datetime import datetime, timedelta, timezone


def get_time():
    """
    Returns a dictionary of the current Date, time, and weekday (for Turkey - Istanbul).
    """
    now = datetime.now(timezone(timedelta(hours=3)))
    return {
        'date': now.strftime('%d.%m.%Y'),
        'timestamp': now.strftime('%H:%M'),
        'weekday': now.weekday() < 5
    }

def now_time():
    '''Returns the current time'''
    now = datetime.now(timezone(timedelta(hours=3)))
    return now.strftime('%H:%M:%S')

def week_business_day_dates():
    '''Returns weekday dates'''
    dates = []
    now = datetime.now(timezone(timedelta(hours=+3)))
    for day in range(now.weekday(), 0, -1):
        dates.append((now - timedelta(days=day)).strftime("%d.%m.%Y"))
    dates.append(now.strftime("%d.%m.%Y"))
    return dates
