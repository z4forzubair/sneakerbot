import datetime

from churchaio.alerts import GENERAL_ALERTS


def check_if_expired(user):
    try:
        expiry_date = user.account.expiry_date
    except Exception:
        msg = GENERAL_ALERTS.get("unknown_error")
    else:
        return True if expiry_date < datetime.date.today() else False
