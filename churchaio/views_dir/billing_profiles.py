from django.contrib import messages
from django.shortcuts import render, redirect

from churchaio.forms import ProfileForm, AddressForm, PaymentForm
from churchaio.models import Profile, Address, Payment


def render_billing(request):
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
        'pay_form': pay_form
    }
    return render(request, 'churchaio/billing_profiles.html', context)


def perform_create_billing(request):
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
                    msg = 'Payment info not valid'
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
                    postal_code=form_data['postal_code'],
                    profile_id=profile.id
                )
            else:
                address.address1 = form_data['address1']
                address.address2 = form_data['address2']
                address.city = form_data['city']
                address.country = form_data['country']
                address.state = form_data['state']
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


def perform_update_billing(request, profile_id):
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


def perform_delete_billing(request, profile_id):
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


def perform_clear_billing(request):
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


def add_favorite_profile(request, profile_id):
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
        except Exception:
            error = ex
            msg = 'Profile could not be updated'
            messages.warning(request, msg)
        else:
            msg = 'Profile updated'

    return redirect('billing')
