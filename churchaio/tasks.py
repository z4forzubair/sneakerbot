from celery import shared_task
from celery.utils.log import get_task_logger

from churchaio.emails import new_user_email, update_subscription_email

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
