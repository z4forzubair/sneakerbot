import stripe
from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import datetime
from dateutil.relativedelta import relativedelta
from churchaio.models import Account

from churchaio.views_dir.billing_profiles import render_billing, perform_create_billing, perform_update_billing, \
    perform_delete_billing, perform_clear_billing, add_favorite_profile
from churchaio.views_dir.proxies import render_proxies, perform_create_proxy_list, perform_create_proxies, \
    perform_delete_proxy, perform_set_proxy_list
from churchaio.views_dir.tasks import render_tasks, perform_create_task, perform_udpate_task, perform_delete_task, \
    perform_clear_tasks, perform_task, perform_all_tasks
from churchaio.views_dir.user_accounts import render_user_profile, perform_user_update, perform_picture_update

stripe.api_key = settings.STRIPE_SECRET_KEY


def success_view(request):
    request.session['_new_user'] = True
    return redirect('login')


def cancel_view(request):
    request.session['_new_user'] = False
    return redirect('login')


class LandingPageView(TemplateView):
    template_name = "churchaio/landing.html"

    def get_context_data(self, **kwargs):
        product_name = "ChurchAIO Bot"
        product_price = 350

        context = super(LandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product_name": product_name,
            "product_price": product_price,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://127.0.0.1:8000/"
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
                            'unit_amount': 35000,
                            'product_data': {
                                'name': 'ChurchAIO Bot',
                            }
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    'product_id': 1,
                },
                mode='payment',
                success_url=YOUR_DOMAIN + 'success/',
                cancel_url=YOUR_DOMAIN + 'cancel/',
            )
            return JsonResponse({
                'id': checkout_session.id
            })
        except Exception as e:
            return str(e)


@csrf_exempt
def stripe_webhook(request):
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

    user_email = session["customer_details"]["email"]
    breakpoint()
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

    send_mail(
        subject="Your New ChurchAIO Bot",
        message=f"Please go to the login url Your ChurchAIO login username is:  {user_name} , and password: {user_password}",
        recipient_list=[user_email],
        from_email="temp@gmail.com"
    )
    print("Fulfilling order")


def index(request):
    return redirect('login')
    # return redirect('landing_page_view')


# user accounts
@login_required(login_url='/login/')
def user_profile(request):
    return render_user_profile(request=request)


@login_required(login_url='/login/')
def update_user_profile(request):
    return perform_user_update(request=request)


@login_required(login_url='/login')
def update_profile_picture(request):
    return perform_picture_update(request=request)


# tasks
@login_required(login_url="/login/")
def tasks(request):
    return render_tasks(request=request)


@login_required(login_url="/login/")
def create_task(request):
    return perform_create_task(request=request)


@login_required(login_url="/login/")
def update_task(request, task_id):
    return perform_udpate_task(request=request, task_id=task_id)


@login_required(login_url='/login/')
def delete_task(request, task_id):
    return perform_delete_task(request=request, task_id=task_id)


@login_required(login_url='/login/')
def clear_tasks(request):
    return perform_clear_tasks(request=request)


# running the tasks


@login_required(login_url='/login/')
def start_task(request, task_id):
    return perform_task(request=request, task_id=task_id)


@login_required(login_url="/login/")
def start_all_tasks(request):
    return perform_all_tasks(request)


# billing profile
@login_required(login_url="/login/")
def billing(request):
    return render_billing(request=request)


@login_required(login_url="/login/")
def create_billing(request):
    perform_create_billing(request=request)


@login_required(login_url="/login/")
def update_billing(request, profile_id):
    return perform_update_billing(request=request, profile_id=profile_id)


@login_required(login_url='/login/')
def delete_billing(request, profile_id):
    return perform_delete_billing(request=request, profile_id=profile_id)


@login_required(login_url='/login/')
def clear_billing(request):
    return perform_clear_billing(request=request)


@login_required(login_url='/login/')
def update_favorite(request, profile_id):
    return add_favorite_profile(request=request, profile_id=profile_id)


# proxies
@login_required(login_url="/login/")
def proxies(request):
    return render_proxies(request=request)


@login_required(login_url="/login/")
def create_proxy_list(request):
    return perform_create_proxy_list(request=request)


@login_required(login_url="/login/")
def create_proxies(request):
    return perform_create_proxies(request=request)


@login_required(login_url='/login/')
def delete_proxy(request, proxy_id):
    return perform_delete_proxy(request=request)


@login_required(login_url='/login/')
def set_proxy_list(request):
    return perform_set_proxy_list(request=request)


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))
