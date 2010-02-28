from datetime import datetime, timedelta

def last_status_date_should_be_now(item):
    delta = (datetime.utcnow() - item.last_status_change_date) 
    assert delta.days == 0 and delta.seconds < 10
