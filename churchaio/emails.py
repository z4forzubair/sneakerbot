from django.core.mail import send_mail
from django.template.loader import render_to_string


def new_user_email(email_context):
    email_subject = render_to_string('email/new_user_subject.txt', email_context)
    email_body = render_to_string('email/new_user_body.txt', email_context)

    send_mail(
        subject=email_subject,
        message=email_body,
        recipient_list=[email_context['user_email']],
        from_email="churchaio@gmail.com"
    )


def update_subscription_email(email_context):
    email_subject = render_to_string("email/update_subscription_subject.txt", email_context)
    email_body = render_to_string("email/update_subscription_body.txt", email_context)

    send_mail(
        subject=email_subject,
        message=email_body,
        recipient_list=[email_context['user_email']],
        from_email="churchaio@gmail.com"
    )
