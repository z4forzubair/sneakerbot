from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render

from churchaio.forms import ProxyListForm, ProxyDropdownForm, ProxyForm
from churchaio.models import ProxyList, Proxy


def render_proxies(request):
    user = request.user
    global proxy_lists
    proxies = None
    count = 0
    proxy_list_id = request.session.get('_proxy_list_id')
    request.session['_proxy_list_id'] = None
    if proxy_list_id is not None:
        try:
            proxy_list = ProxyList.objects.filter(user_id=user.id).get(id=int(proxy_list_id))
            proxies = proxy_list.proxy_set.all().order_by("created_at")
            count = proxies.count()
        except Proxy.DoesNotExist:
            msg = 'no proxies found'
    form = ProxyForm(request.POST or None)
    proxy_list_form = ProxyListForm(request.POST or None)
    proxy_dropdown = ProxyDropdownForm(request.POST or None, user=user)
    context = {
        'segment': 'proxies',
        'proxies': proxies,
        'count': count,
        'form': form,
        'proxy_list_form': proxy_list_form,
        'proxy_dropdown': proxy_dropdown
    }

    return render(request, 'churchaio/proxies.html', context=context)


def perform_create_proxy_list(request):
    global proxy_list
    user = request.user
    name = request.GET.get('name')
    msg = None
    try:
        pl = ProxyList.objects.filter(user_id=user.id, name=name)
        if len(pl) > 0:
            proxy_count = len(pl[0].proxy_set.all())
            if proxy_count == 0:
                pl.delete()
        proxy_list = ProxyList(
            name=name,
            user_id=user.id
        )
        proxy_list.save()
    except Exception:
        msg = 'Proxy List could not be created due to some error!'

    if proxy_list.id is not None:
        proxy_list_id = str(proxy_list.id)
        request.session['_proxy_list_id'] = proxy_list_id
    data = {
        'msg': msg
    }
    return JsonResponse(data)


def save_proxies(first_split, pl):
    error = None
    try:
        with transaction.atomic():
            for i in first_split:
                sec_split = i.split(':')
                proxy = Proxy(
                    ip_address=sec_split[0],
                    port=sec_split[1],
                    username=sec_split[2],
                    password=sec_split[3],
                    proxy_list_id=pl.id
                )
                proxy.save()
    except Exception as ex:
        error = ex
        msg = 'Proxies could not be saved'
    else:
        msg = 'All proxies added'
    return error, msg


def perform_create_proxies(request):
    global error, msg
    user = request.user
    if request.method == 'POST':
        form = ProxyForm(request.POST or None)
        if form.is_valid():
            form_data = form.cleaned_data
            proxies = form_data.get('proxies')
            try:
                pl = ProxyList.objects.filter(user_id=user.id).last()
            except Exception as ex:
                error = ex
                msg = 'Proxy List could not be found'
            else:
                first_split = proxies.split('\r\n') if '\r\n' in proxies else proxies.split('\n')
                error, msg = save_proxies(first_split, pl)
    if error is None:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)
    return redirect('proxies')


def perform_delete_proxy(request):
    if request.method == 'POST':
        try:
            # issue here with proxy
            proxy = Proxy.objects.get(id=proxy_id)
            proxy_list_id = str(proxy.proxy_list.id)
            request.session['_proxy_list_id'] = proxy_list_id
        except Proxy.DoesNotExist:
            msg = 'The proxy does not exist'
            messages.warning(request, msg)
        else:
            try:
                proxy.delete()
            except Exception:
                msg = 'Proxy could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'Proxy deleted!'
                messages.warning(request, msg)

    return redirect('proxies')


def perform_set_proxy_list(request):
    proxy_list_id = request.POST.get('proxy_list')
    request.session['_proxy_list_id'] = proxy_list_id
    return redirect('proxies')
