from django.contrib.auth.decorators import login_required
from django import template
from django.http import HttpResponse
from django.template import loader

from churchaio.views_dir.user_accounts import render_user_profile, perform_user_update, perform_picture_update
from churchaio.views_dir.tasks import render_tasks, perform_create_task, perform_udpate_task, perform_delete_task, \
    perform_clear_tasks, perform_task, perform_all_tasks
from churchaio.views_dir.billing_profiles import render_billing, perform_create_billing, perform_update_billing, \
    perform_delete_billing, perform_clear_billing, add_favorite_profile
from churchaio.views_dir.proxies import render_proxies, perform_create_proxy_list, perform_create_proxies, \
    perform_delete_proxy, perform_set_proxy_list


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


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
