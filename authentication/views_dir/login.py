import secrets

from django_user_agents.utils import get_user_agent

from authentication.models import Login
from churchaio.alerts import LOGIN_ALERTS, GENERAL_ALERTS


def get_cookie():
    return secrets.token_hex(nbytes=16)


def login_helper(request, user):
    cookie_value = request.COOKIES.get('p_usr_login')
    user_agent = get_user_agent(request)

    if cookie_value is not None:
        try:
            user_login = user.login
        except Login.DoesNotExist:
            return False, GENERAL_ALERTS.get("unknown_error")
        else:
            if cookie_value == user_login.cookie:
                return True, None
            else:
                return False, LOGIN_ALERTS.get("cookie_mismatch")
            # to check also that the relevant user_agent_logged_in is False/None
            # and to make the user_agent_logged_in False/None on logout
    else:  # cookie is None in request browser
        try:
            user_login = user.login
        except Login.DoesNotExist:  # logging in for the first time
            user_login = Login(
                user_id=user.id,
                cookie=get_cookie(),
                pc=user_agent.is_pc,
                mobile=user_agent.is_mobile,
                tablet=user_agent.is_tablet,
                is_logged_in=True
            )
        else:  # not logging in for the first time, but cookie NOT present => maybe a different user_agent
            if user_agent.is_pc:
                if user_login.pc:
                    return False, LOGIN_ALERTS.get("dual_login")
                else:
                    user_login.pc = True
            elif user_agent.is_mobile:
                if user_login.mobile:
                    return False, LOGIN_ALERTS.get("dual_login")
                else:
                    user_login.mobile = True
            elif user_agent.is_tablet:
                if user_login.tablet:
                    return False, LOGIN_ALERTS.get("dual_login")
                else:
                    user_login.tablet = True
        try:
            user_login.save()
        except Exception:
            return False, GENERAL_ALERTS.get("unknown_error")
        else:
            return True, user_login.cookie
