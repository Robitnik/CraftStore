from datetime import date

def get_today_date():
    return date.today()
def get_today_date_formatted():
    return get_today_date().strftime('%Y-%m-%d')  # формат: рік-місяць-день
