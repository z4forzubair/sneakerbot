import celery.result
from celery import shared_task
from celery.utils.log import get_task_logger

from churchaio.celery_helpers.emails import new_user_email, update_subscription_email
from churchaio.celery_helpers.footlocker import footlocker_bot
from churchaio.celery_helpers.jd_sports import jd_sports_bot

logger = get_task_logger(__name__)


@shared_task()
def new_user_email_task(email_context):
    """sends an email when user pays successfully"""
    logger.info("Sent new user email")
    return new_user_email(email_context=email_context)


@shared_task()
def update_subscription_email_task(email_context):
    """sends an email when user resubscribes successfully"""
    logger.info("Sent resubscribe email")
    return update_subscription_email(email_context=email_context)


# used_id for discord webhook
@shared_task()
def footlocker_bot_task(task_id, user_id):
    return footlocker_bot(task_id=task_id)


@shared_task()
def jd_sports_bot_task(task_id, user_id):
    return jd_sports_bot(task_id=task_id)
