import stripe
from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from churchaio.views_dir.billing_profiles import render_billing, perform_create_billing, perform_update_billing, \
    perform_delete_billing, perform_clear_billing, add_favorite_profile
from churchaio.views_dir.helper_views import check_if_expired
from churchaio.views_dir.proxies import render_proxies, perform_create_proxy_list, perform_create_proxies, \
    perform_delete_proxy, perform_set_proxy_list, perform_clear_proxy_list
from churchaio.views_dir.stripe import create_checkout_session, trigger_stripe_webhook
from churchaio.views_dir.tasks import render_tasks, perform_create_task, perform_udpate_task, perform_delete_task, \
    perform_clear_tasks, perform_task, perform_all_tasks
from churchaio.views_dir.user_accounts import render_user_profile, perform_user_update, perform_picture_update

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        price = 35000 if product_id == '1' else 6000
        return create_checkout_session(product_id, price)


@csrf_exempt
def stripe_webhook(request):
    return trigger_stripe_webhook(request=request, settings=settings)


def success_view(request, product_id):
    if product_id == 1:
        request.session['_new_user'] = True
    else:
        request.session['_new_sub'] = True
    return redirect('login')


def cancel_view(request, product_id):
    if product_id == 1:
        request.session['_new_user'] = False
    else:
        request.session['_new_sub'] = False
    return redirect('login')


class LandingPageView(TemplateView):
    template_name = "churchaio/landing.html"

    def render_to_response(self, context, **response_kwargs):
        response = super(LandingPageView, self).render_to_response(context, **response_kwargs)
        cookie = self.request.session.get('p_usr_login')
        if cookie is not None:
            self.request.session['p_usr_login'] = None
            response.set_cookie('p_usr_login', cookie)
        return response

    def get_context_data(self, **kwargs):
        product_name = "ChurchAIO Bot"
        product_price = 350

        context = super(LandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product_name": product_name,
            "product_price": product_price,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            "product_id": 1
        })
        return context


def index(request):
    return redirect('landing_page_view')


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
    if check_if_expired(request.user):
        request.session["expired"] = True
        return redirect("logout")
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
    return perform_delete_proxy(request=request, proxy_id=proxy_id)


@login_required(login_url='/login/')
def set_proxy_list(request):
    return perform_set_proxy_list(request=request)


@login_required(login_url='/login/')
def clear_proxy_list(request):
    return perform_clear_proxy_list(request=request)


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
