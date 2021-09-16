from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from churchaio.forms import UserForm, ConfigurationForm, AccountForm, PictureForm
from churchaio.models import Configuration, Picture, Account


def render_user_profile(request):
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
    html_template = loader.get_template('page-user.html')
    response = HttpResponse(html_template.render(context, request))
    cookie = request.session.get('p_usr_login')
    if cookie is not None:
        request.session['p_usr_login'] = None
        response.set_cookie('p_usr_login', cookie)
    return response


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
                webhook=None if form_data['webhook'] == '' else form_data['webhook'],
                auto_solve=None if form_data['auto_solve'] == '' else form_data['auto_solve'],
                sleep=5,
                user_id=user.id
            )
        else:
            config.timeout = form_data['timeout']
            config.retry = form_data['retry']
            config.monitor = form_data['monitor']
            config.webhook = None if form_data['webhook'] == '' else form_data['webhook']
            config.auto_solve = None if form_data['auto_solve'] == '' else form_data['auto_solve']
        try:
            config.save()
        except Exception:
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
        except Exception:
            msg = 'User account update failed'
            messages.warning(request, msg)
        else:
            user.refresh_from_db()
            update_complete_status(user=user)
            msg = 'saved'
    else:
        msg = 'User account form is invalid'
        messages.warning(request, msg)


def perform_user_update(request):
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
            except Exception:
                msg = 'User update failed'
                messages.warning(request, msg)
            else:
                update_account(request, account_form)
                update_config(request, config_form)
        else:
            msg = 'User form is invalid'
            messages.warning(request, msg)
    return redirect('userProfile')


def perform_picture_update(request):
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
            msg = 'Profile picture could not be uploaded'
            messages.warning(request, msg)
        else:
            user.refresh_from_db()
            update_complete_status(user=user)

    return redirect('userProfile')
