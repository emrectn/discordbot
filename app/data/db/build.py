import pandas as pd

from lib.db import mongo
from lib.utils.clock import get_time, week_business_day_dates


def build_structure(user, report):
    """
    Build the structure of the database
    """
    date, time, _ = get_time().values()
    return{
        'info': {
            'user_id': user.id,
            'user_name': user.name,
            'date': date,
            'time': time,
        },
        
        'report': report
    }
    

def get_daily_reports():
    """
    Get all daily reports from the database
    """
    data = mongo.daily_db.reports.find({'info.date': get_time()['date']}, {'_id': 0})
    if data.count() > 0:
        return data


def list_of_reports():
    """
    Get all daily reports from the database
    """
    reported_users = mongo.daily_db.reports.find({'info.date': get_time()['date']})
    return [user['info']['user_id'] for user in reported_users]


def daily_reports_df():
    """
    Create a DataFrame of current Dates reports
    """
    info_collection = [i['info'] for i in mongo.daily_db.reports.find({'info.date': get_time()['date']})]
    report_collection = [i['report'] for i in mongo.daily_db.reports.find({'info.date': get_time()['date']})]

    df1, df2 = pd.DataFrame(list(info_collection)), pd.DataFrame(list(report_collection))

    if df1.empty or df2.empty:
        df = pd.DataFrame()
    else:
        df = pd.concat([df1, df2], axis=1).drop(columns='user_id')
    
    return df


def get_weekly_data(user_id):
    week_dates = week_business_day_dates()
    return pd.json_normalize(
        [i for i in mongo.daily_db.reports.find(
            {"info.user_id": user_id, "info.date": {"$in": week_dates}},
            {"_id": 0, "info.date": 1, "report": 1})]
    ), week_dates
