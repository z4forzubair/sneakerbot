import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse

import stripe
from churchaio.models import Account
from churchaio.tasks import new_user_email_task, update_subscription_email_task


def create_checkout_session(product_id, price):
    YOUR_DOMAIN = "http://localhost:8000/"
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=[
                'card',
            ],
            line_items=[
                {
                    # TODO: replace this with the `price` of the product you want to sell
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': price,
                        'product_data': {
                            'name': 'ChurchAIO Bot',
                        }
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'product_id': product_id,
            },
            mode='payment',
            success_url=YOUR_DOMAIN + f'success/{product_id}/',
            cancel_url=YOUR_DOMAIN + f'cancel/{product_id}/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })
    except Exception as e:
        return str(e)


def trigger_stripe_webhook(request, settings):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Fulfill the purchase...
        fulfill_order(session)

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(session):
    # TODO: fill me in

    product_id = session["metadata"]["product_id"]
    if product_id == "1":
        new_user(session=session)

    else:
        update_subscription(session)


def new_user(session):
    user_email = session["customer_details"]["email"]
    user_name = user_email.split('@')[0].replace('.', '')
    # create_password
    user_password = "Abc123."
    user = None
    try:
        user = User.objects.create(
            username=user_name,
            email=user_email,
            password=user_password
        )
    except Exception:
        msg = "User could not be saved"

    try:
        user_password = User.objects.make_random_password()
        user.set_password(user_password)
        user.save(update_fields=['password'])
    except Exception:
        msg = 'Password update failed'

    today = datetime.date.today()
    two_m_after = today + relativedelta(months=2)
    try:
        account = Account.objects.create(
            expiry_date=two_m_after,
            user_id=user.id
        )
    except Exception:
        msg = 'Expiry date could not be updated'

    login_url = 'http://localhost:8000/login/'
    email_context = {
        'user_email': user_email,
        'user_name': user_name,
        'user_password': user_password,
        'login_url': login_url
    }
    new_user_email_task.delay(email_context)
    print("Fulfilling new order")


def update_subscription(session):
    user_email = session["customer_details"]["email"]
    user = None
    try:
        user = User.objects.filter(email=user_email).first()
    except Exception:
        msg = "User does not exist"

    today = datetime.date.today()
    one_m_after = today + relativedelta(months=1)
    try:
        account = user.account
        account.expiry_date = one_m_after
        account.save(update_fields=['expiry_date'])
    except Exception:
        msg = 'Expiry date could not be updated'

    email_context = {
        'user_email': user_email
    }
    update_subscription_email_task.delay(email_context)
    print("Adding subscription")
