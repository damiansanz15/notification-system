from datetime import datetime, timedelta
from util.messages import months_names

LOCAL_DATE_FORMAT = "%d/%m/%Y"

def add_days_to_date(no_days, original_date):
    days_to_add = timedelta(days=no_days)
    new_date = datetime.strptime(original_date,LOCAL_DATE_FORMAT).date()
    return new_date + days_to_add


def get_today_date_str():
    now = datetime.now()
    return now.strftime(LOCAL_DATE_FORMAT)

def get_today_date():
    now = datetime.today().date()
    return now

def get_today_date_minus_one_day():
    now = datetime.today().date()
    one_day_before = now - timedelta(days=1)
    return one_day_before

def get_month():
    return months_names.get(datetime.now().strftime("%B"))

def get_year():
    return datetime.now().year


def db_date_to_local_date(date):
    return datetime.strptime(date,LOCAL_DATE_FORMAT).date()

def string_to_local_date(date):
    return datetime.strptime(date,LOCAL_DATE_FORMAT).date()
