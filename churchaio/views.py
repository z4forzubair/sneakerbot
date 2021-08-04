from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib import messages
from django import template
from .forms import *
from .bots.footlocker import *


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url='/login/')
def userProfile(request):
    user = request.user
    user_form = UserForm(request.POST or None, user=user)
    try:
        config = user.configuration
    except Configuration.DoesNotExist:
        msg = 'no configuration'
        config_form = ConfigurationForm(request.POST or None, user=user)
    else:
        config_form = ConfigurationForm(request.POST or None, user=user, instance=config)
    try:
        account = user.account
    except Account.DoesNotExist:
        msg = 'no account'
        account_form = AccountForm(request.POST or None, user=user)
    else:
        account_form = AccountForm(request.POST or None, user=user, instance=account)
    picture_form = PictureForm()

    context = {
        'segment': 'userprofile',
        'user_form': user_form,
        'config_form': config_form,
        'account_form': account_form,
        'picture_form': picture_form
    }
    return render(request, 'page-user.html', context=context)


def update_config(request, config_form):
    user = request.user
    if config_form.is_valid():
        form_data = config_form.cleaned_data
        try:
            config = user.configuration
        except Configuration.DoesNotExist:
            config = Configuration(
                timeout=form_data['timeout'],
                retry=form_data['retry'],
                monitor=form_data['monitor'],
                sleep=5,
                user_id=user.id
            )
        else:
            config.timeout = form_data['timeout']
            config.retry = form_data['retry']
            config.monitor = form_data['monitor']
        try:
            config.save()
        except Exception as ex:
            msg = 'User Configurations update failed'
            messages.warning(request, msg)
        else:
            msg = 'Saved successfully'
            messages.success(request, msg)
    else:
        msg = 'The form is invalid'
        messages.warning(request, msg)


def update_complete_status(user):
    try:
        picture = user.picture
    except Picture.DoesNotExist:
        msg = 'Picture not found'
    else:
        try:
            account = user.account
        except Account.DoesNotExist:
            msg = 'Account not found'
        else:
            if account.phone_number is not None:
                account.complete_status = True
                try:
                    account.save()
                except Exception as ex:
                    msg = 'Could not update account status'


def update_account(request, account_form):
    user = request.user
    if account_form.is_valid():
        form_data = account_form.cleaned_data
        try:
            account = user.account
        except Account.DoesNotExist:
            account = Account(
                sex=form_data['sex'],
                phone_number=form_data['phone_number'],
                complete_status=False,
                user_id=user.id
            )
        else:
            account.sex = form_data['sex']
            account.phone_number = form_data['phone_number']
        try:
            account.save()
        except Exception as ex:
            msg = 'User account update failed'
            messages.warning(request, msg)
        else:
            user.refresh_from_db()
            update_complete_status(user=user)
            msg = 'saved'
    else:
        msg = 'User account form is invalid'
        messages.warning(request, msg)


@login_required(login_url='/login/')
def updateUserProfile(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, user=user)
        config_form = ConfigurationForm(request.POST, user=user)
        account_form = AccountForm(request.POST, user=user)
        if user_form.is_valid():
            form_data = user_form.cleaned_data
            user.first_name = form_data.get('first_name')
            user.last_name = form_data.get('last_name')
            try:
                user.save()
            except Exception as ex:
                msg = 'User update failed'
                messages.warning(request, msg)
            else:
                update_account(request, account_form)
                update_config(request, config_form)
        else:
            msg = 'User form is invalid'
            messages.warning(request, msg)
    return redirect('userProfile')


@login_required(login_url='/login')
def updateProfilePicture(request):
    user = request.user
    picture_form = PictureForm(request.POST, files=request.FILES)
    if picture_form.is_valid():
        form_data = picture_form.cleaned_data
        try:
            picture = user.picture
        except Picture.DoesNotExist:
            picture = Picture(
                picture=form_data['picture'],
                user_id=user.id
            )
        else:
            picture.picture = form_data['picture']
        try:
            picture.save()
        except Exception as ex:
            msg = 'Profile picture could not be uplaoded'
            messages.warning(request, msg)
        else:
            user.refresh_from_db()
            update_complete_status(user=user)

    return redirect('userProfile')


@login_required(login_url="/login/")
def startAllTasks(request):
    # checkout()
    return redirect('tasks')


def failedTaskMessage(request):
    msg = 'The task failed'
    messages.warning(request, msg)


@login_required(login_url='/login/')
def startTask(request, task_id):
    try:
        task = Task.objects.filter(user_id=request.user.id).get(id=task_id)
    except Task.DoesNotExist:
        error = 'error'
        msg = 'The task does not exist'
        messages.warning(request, msg)
    else:
        if task.status == Task.STATUS.MATURE:
            url = task.sku_link
            bot = FootlockerBot(url=url, task=task)
            if bot.returnStatus():
                if bot.addToCart():
                    # add to cart successful
                    if bot.checkout():
                        msg = 'Successfully purchased'
                        messages.success(request, msg)
                    else:
                        failedTaskMessage(request)
                else:
                    failedTaskMessage(request)
            else:
                failedTaskMessage(request)
        else:
            msg = 'Cannot execute this task'
            messages.warning(request, msg)

    return redirect('tasks')


def tasks_render(form, request, msg=None, error=None):
    user = request.user
    tasks_list = Task.objects.filter(user=user).order_by('-created_at')
    count = tasks_list.count()
    forms_list = []
    for task in tasks_list:
        edit_form = TaskForm(user=user, instance=task)
        forms_list.append(edit_form)

    edit_tasks_list = zip(tasks_list, forms_list)
    context = {
        'segment': 'tasks',
        'edit_tasks_list': edit_tasks_list,
        'count': count,
        'form': form,
        'msg': msg
    }
    return render(request, 'churchaio/tasks.html', context)


@login_required(login_url="/login/")
def tasks(request):
    old_task = request.session.get('_old_task')
    form = TaskForm(old_task or None, user=request.user)
    request.session['_old_task'] = None
    return tasks_render(form=form, request=request)


def matureTaskStatus(task, proxy_list, profile):
    task_status = task.status
    task.status = Task.STATUS.MATURE if proxy_list is not None and profile is not None else Task.STATUS.IMMATURE
    if task.status != task_status:
        error = None
        msg = None
        try:
            task.save()
        except Exception as ex:
            error = ex
            msg = 'Could not mature task status'
        else:
            msg = 'Task status matured'


@login_required(login_url="/login/")
def createTask(request):
    user = request.user
    form = TaskForm(request.POST, user=user)
    msg = None
    error = None
    if request.method == 'POST':
        if form.is_valid():
            form_data = form.cleaned_data
            try:
                task_count = form_data['task_count']
                for i in range(0, task_count):
                    task = Task(
                        store_name=form_data['store_name'],
                        shoe_size=form_data['shoe_size'] or -1,
                        sku_link=form_data['sku_link'],
                        proxy_list_id=form_data['proxy_list'].id if form_data['proxy_list'] is not None else None,
                        profile_id=form_data['profile'].id if form_data['profile'] is not None else None,
                        user_id=user.id
                    )
                    task.save()
                    matureTaskStatus(task, form_data['proxy_list'], form_data['profile'])
            except Exception as ex:
                error = ex
                msg = 'Task could not be created'
                messages.warning(request, msg)
            else:
                msg = 'Task created successfully'
                messages.success(request, msg)
        else:
            error = 'Invalid form'
            msg = 'Task could not be created'
            messages.warning(request, msg)
    if error is not None:
        request.session['_old_task'] = request.POST
    return redirect('tasks')


@login_required(login_url="/login/")
def updateTask(request, task_id):
    user = request.user
    msg = None
    error = None
    if request.method == 'POST':
        try:
            task = Task.objects.filter(user_id=user.id).get(id=task_id)
        except Task.DoesNotExist:
            error = 'error'
            msg = 'The task does not exist'
            messages.warning(request, msg)
        else:
            form = TaskForm(request.POST, user=user)
            if form.is_valid():
                form_data = form.cleaned_data
                task.store_name = form_data['store_name']
                task.shoe_size = form_data['shoe_size'] or -1
                task.sku_link = form_data['sku_link']
                task.proxy_list_id = form_data['proxy_list'].id if form_data['proxy_list'] is not None else None
                task.profile_id = form_data['profile'].id if form_data['profile'] is not None else None
                try:
                    task.save()
                    matureTaskStatus(task, form_data['proxy_list'], form_data['profile'])
                except Exception as ex:
                    error = ex
                    msg = 'Task could not be updated'
                    messages.warning(request, msg)
                else:
                    msg = 'Task updated successfully'
                    messages.success(request, msg)
            else:
                error = 'Invalid form'
                msg = 'Task could not be updated'
                messages.warning(request, msg)

    return redirect('tasks')


@login_required(login_url='/login/')
def deleteTask(request, task_id):
    msg = None
    error = None
    if request.method == 'POST':
        try:
            task = Task.objects.filter(user_id=request.user).get(id=task_id)
        except Task.DoesNotExist:
            error = 'error'
            msg = 'The task does not exist'
            messages.warning(request, msg)
        else:
            try:
                task.delete()
            except Exception as ex:
                error = ex
                msg = 'Task could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'Task deleted!'
                messages.warning(request, msg)

    return redirect('tasks')


@login_required(login_url='/login/')
def clearTasks(request):
    error = None
    msg = None
    if request.method == 'POST':
        try:
            tasks = Task.objects.filter(user_id=request.user)
        except Task.DoesNotExist:
            msg = 'No tasks to delete'
            messages.warning(request, msg)
        else:
            try:
                tasks.delete()
            except Exception as ex:
                error = ex
                msg = 'Tasks could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'All tasks cleared!'
                messages.warning(request, msg)

    return redirect('tasks')


# billing starts here
def billing_render(request, msg=None, error=None):
    user = request.user
    # create forms
    old_billing = request.session.get('_old_billing')
    profile_form = ProfileForm(old_billing or None, user=request.user)
    address_form = AddressForm(old_billing or None, user=request.user)
    pay_form = PaymentForm(old_billing or None, user=request.user)
    request.session['_old_billing'] = None

    profiles_list = Profile.objects.filter(user=user).order_by('-created_at')
    count = profiles_list.count()
    profile_forms_list = []
    address_forms_list = []
    pay_forms_list = []
    for profile in profiles_list:
        address_instance = None
        payment_instance = None
        try:
            address_instance = profile.address
        except Address.DoesNotExist:
            ea = 'No address for profile'
        try:
            payment_instance = profile.payment
        except Payment.DoesNotExist:
            ep = 'No paycard for profile'
        edit_profile_form = ProfileForm(user=user, instance=profile)
        edit_address_form = AddressForm(user=user, instance=address_instance)
        edit_pay_form = PaymentForm(user=user, instance=payment_instance)
        profile_forms_list.append(edit_profile_form)
        address_forms_list.append(edit_address_form)
        pay_forms_list.append(edit_pay_form)

    edit_profiles_list = zip(profiles_list, profile_forms_list, address_forms_list, pay_forms_list)
    context = {
        'segment': 'profiles',
        'edit_profiles_list': edit_profiles_list,
        'count': count,
        'profile_form': profile_form,
        'address_form': address_form,
        'pay_form': pay_form,
        'msg': msg
    }
    return render(request, 'churchaio/billing_profiles.html', context)


@login_required(login_url="/login/")
def billing(request):
    return billing_render(request=request)


@login_required(login_url="/login/")
def createBilling(request):
    user = request.user
    profile_form = ProfileForm(request.POST, user=user)
    address_form = AddressForm(request.POST, user=user)
    pay_form = PaymentForm(request.POST, user=user)
    profile = None
    msg = None
    error = None
    if request.method == 'POST':
        if profile_form.is_valid():
            form_data = profile_form.cleaned_data
            try:
                profile = Profile(
                    name=form_data['name'],
                    first_name=form_data['first_name'],
                    last_name=form_data['last_name'],
                    email=form_data['email'],
                    salutation=form_data['salutation'],
                    contact=form_data['contact'],
                    day=form_data['day'],
                    month=form_data['month'],
                    year=form_data['year'],
                    user_id=user.id
                )
                profile.save()
            except Exception as ex:
                error = ex
                msg = 'Profile could not be created'
                messages.warning(request, msg)
            else:
                msg = 'Profile created successfully'
                messages.success(request, msg)
                # address_form
                if address_form.is_valid():
                    form_data = address_form.cleaned_data
                    try:
                        address = Address(
                            address1=form_data['address1'],
                            address2=form_data['address2'],
                            city=form_data['city'],
                            country=form_data['country'],
                            state=form_data['state'],
                            zip_code=form_data['zip_code'],
                            postal_code=form_data['postal_code'],
                            profile_id=profile.id
                        )
                        address.save()
                    except Exception as ex:
                        error = ex
                        msg = 'Delivery Address could not be saved'
                        messages.warning(request, msg)
                else:
                    error = 'Invalid address form'
                    msg = 'Delivery form is invalid'
                    messages.warning(request, msg)
                # pay form
                if pay_form.is_valid():
                    form_data = pay_form.cleaned_data
                    try:
                        payment = Payment(
                            pay_type=form_data['pay_type'],
                            cc_number=form_data['cc_number'],
                            cc_expiry=form_data['cc_expiry'],
                            cc_code=form_data['cc_code'],
                            profile_id=profile.id
                        )
                        payment.save()
                    except Exception as ex:
                        error = ex
                        msg = 'Payment info could not be saved'
                        messages.warning(request, msg)
                else:
                    error = 'Invalid payment form'
                    msg = 'Address could not be saved'
                    messages.warning(request, msg)
        else:
            error = 'Invalid profile form'
            msg = 'Profile could not be created'
            messages.warning(request, msg)

    if error is not None:
        request.session['_old_billing'] = request.POST
    return redirect('billing')


def save_address(profile, request, address=None):
    address_form = AddressForm(request.POST, user=request.user)
    if address_form.is_valid():
        form_data = address_form.cleaned_data
        try:
            if address is None:
                address = Address(
                    address1=form_data['address1'],
                    address2=form_data['address2'],
                    city=form_data['city'],
                    country=form_data['country'],
                    state=form_data['state'],
                    zip_code=form_data['zip_code'],
                    postal_code=form_data['postal_code'],
                    profile_id=profile.id
                )
            else:
                address.address1 = form_data['address1']
                address.address2 = form_data['address2']
                address.city = form_data['city']
                address.country = form_data['country']
                address.state = form_data['state']
                address.zip_code = form_data['zip_code']
                address.postal_code = form_data['postal_code']
            address.save()
        except Exception as ex:
            error = ex
            msg = 'Delivery Address could not be saved'
            messages.warning(request, msg)
    else:
        error = 'Invalid address form'
        msg = 'Address could not be saved'
        messages.warning(request, msg)


def update_address(profile, request):
    msg = None
    error = None
    try:
        address = profile.address
    except Address.DoesNotExist:
        # create new address
        save_address(profile, request)
    else:
        save_address(profile, request, address)


def save_payment(profile, request, payment=None):
    payment_form = PaymentForm(request.POST, user=request.user)
    if payment_form.is_valid():
        form_data = payment_form.cleaned_data
        try:
            if payment is None:
                payment = Payment(
                    pay_type=form_data['pay_type'],
                    cc_number=form_data['cc_number'],
                    cc_expiry=form_data['cc_expiry'],
                    cc_code=form_data['cc_code'],
                    profile_id=profile.id
                )
            else:
                payment.pay_type = form_data['pay_type']
                payment.cc_number = form_data['cc_number']
                payment.cc_expiry = form_data['cc_expiry']
                payment.cc_code = form_data['cc_code']
            payment.save()
        except Exception as ex:
            error = ex
            msg = 'Payment info could not be saved'
            messages.warning(request, msg)
    else:
        error = 'Invalid payment form'
        msg = 'Payment could not be saved'
        messages.warning(request, msg)


def update_payment(profile, request):
    msg = None
    error = None
    try:
        payment = profile.payment
    except Payment.DoesNotExist:
        # create new payment
        save_payment(profile, request)
    else:
        save_payment(profile, request, payment)


@login_required(login_url="/login/")
def updateBilling(request, profile_id):
    user = request.user
    msg = None
    error = None
    if request.method == 'POST':
        try:
            profile = Profile.objects.filter(user_id=user.id).get(id=profile_id)
        except Profile.DoesNotExist:
            error = 'error'
            msg = 'The profile does not exist'
            messages.warning(request, msg)
        else:
            form = ProfileForm(request.POST, user=user)
            if form.is_valid():
                form_data = form.cleaned_data
                profile.name = form_data['name']
                profile.first_name = form_data['first_name']
                profile.last_name = form_data['last_name']
                profile.email = form_data['email']
                profile.salutation = form_data['salutation']
                profile.contact = form_data['contact']
                profile.day = form_data['day']
                profile.month = form_data['month']
                profile.year = form_data['year']
                try:
                    profile.save()
                except Exception as ex:
                    error = ex
                    msg = 'Profile could not be updated'
                    messages.warning(request, msg)
                else:
                    update_address(profile, request)
                    update_payment(profile, request)
                    msg = 'Profile updated successfully'
                    messages.success(request, msg)
            else:
                error = 'Invalid form'
                msg = 'Profile could not be updated'
                messages.warning(request, msg)

    return redirect('billing')


@login_required(login_url='/login/')
def deleteBilling(request, profile_id):
    msg = None
    error = None
    if request.method == 'POST':
        try:
            profile = Profile.objects.filter(user_id=request.user).get(id=profile_id)
        except Profile.DoesNotExist:
            error = 'error'
            msg = 'The profile does not exist'
            messages.warning(request, msg)
        else:
            try:
                profile.delete()
            except Exception as ex:
                error = ex
                msg = 'Profile could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'Profile deleted!'
                messages.warning(request, msg)

    return redirect('billing')


@login_required(login_url='/login/')
def clearBilling(request):
    error = None
    msg = None
    if request.method == 'POST':
        try:
            profiles = Profile.objects.filter(user_id=request.user)
        except Profile.DoesNotExist:
            msg = 'No profiles to delete'
            messages.warning(request, msg)
        else:
            try:
                profiles.delete()
            except Exception as ex:
                error = ex
                msg = 'Profiles could not be deleted'
                messages.warning(request, msg)
            else:
                msg = 'All Profiles cleared!'
                messages.warning(request, msg)

    return redirect('billing')


@login_required(login_url='/login/')
def updateFavorite(request, profile_id):
    msg = None
    error = None
    try:
        profile = Profile.objects.filter(user_id=request.user).get(id=profile_id)
    except Profile.DoesNotExist:
        error = 'error'
        msg = 'The profile does not exist'
        messages.warning(request, msg)
    else:
        try:
            profile.favorite = True if profile.favorite == False else False
            profile.save()
        except Exception as ex:
            error = ex
            msg = 'Profile could not be updated'
            messages.warning(request, msg)
        else:
            msg = 'Profile updated'

    return redirect('billing')


@login_required(login_url="/login/")
def proxies(request):
    user = request.user
    global proxy_lists
    proxies = None
    proxy_list_id = request.session.get('_proxy_list_id')
    request.session['_proxy_list_id'] = None
    if proxy_list_id is not None:
        try:
            proxy_list = ProxyList.objects.filter(user_id=user.id).get(id=int(proxy_list_id))
            proxies = proxy_list.proxy_set.all().order_by("created_at")
        except Proxy.DoesNotExist:
            msg = 'no proxies found'
    form = ProxyForm(request.POST or None)
    proxy_list_form = ProxyListForm(request.POST or None)
    proxy_dropdown = ProxyDropdownForm(request.POST or None, user=user)
    context = {
        'segment': 'proxies',
        'proxies': proxies,
        'form': form,
        'proxy_list_form': proxy_list_form,
        'proxy_dropdown': proxy_dropdown
    }

    return render(request, 'churchaio/proxies.html', context=context)


@login_required(login_url='/login/')
def setProxyList(request):
    proxy_list_id = request.POST.get('proxy_list')
    request.session['_proxy_list_id'] = proxy_list_id
    return redirect('proxies')


@login_required(login_url="/login/")
def createProxyList(request):
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
    except Exception as ex:
        msg = 'Proxy List could not be created due to some error!'

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


@login_required(login_url="/login/")
def createProxies(request):
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


@login_required(login_url='/login/')
def deleteProxy(request, proxy_id):
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
