from datetime import datetime, timedelta

def check_last_status_date(item):
    delta = (datetime.utcnow() - item.last_status_change_date) 
    assert delta.days == 0 and delta.seconds < 10