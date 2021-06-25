from django import forms

from churchaio.models import *
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField


# user will be the current user for all forms
class TaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.task = kwargs.pop('instance', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['proxy_list'].queryset = ProxyList.objects.filter(user=self.user)
        self.fields['profile'].queryset = Profile.objects.filter(user=self.user)
        if self.task is not None:
            self.fields['store_name'].initial = self.task.store_name
            self.fields['shoe_size'].initial = self.task.shoe_size if self.task.shoe_size != -1 else None
            self.fields['sku_link'].initial = self.task.sku_link
            self.fields['profile'].initial = self.task.profile
            self.fields['proxy_list'].initial = self.task.proxy_list
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    store_name = forms.CharField(max_length=50)
    shoe_size = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Random'
            }
        ), required=False)
    sku_link = forms.URLField(max_length=120)
    task_count = forms.IntegerField(initial=1)
    proxy_list = forms.ModelChoiceField(queryset=None, required=False, empty_label='Proxy List')
    profile = forms.ModelChoiceField(queryset=None, required=False, empty_label='Profile')


class ProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.profile = kwargs.pop('instance', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.profile is not None:
            self.fields['name'].initial = self.profile.name
            self.fields['first_name'].initial = self.profile.first_name
            self.fields['last_name'].initial = self.profile.last_name
            self.fields['email'].initial = self.profile.email
            self.fields['salutation'].initial = self.profile.salutation
            self.fields['contact'].initial = self.profile.contact
            self.fields['day'].initial = self.profile.day
            self.fields['month'].initial = self.profile.month
            self.fields['year'].initial = self.profile.year
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    name = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    DUMMY = '---------'
    MR = 'MR'
    MS = 'MS'
    SALUTATION_CHOICES = (
        (MR, 'Mr'),
        (MS, 'Ms'),
    )
    salutation = forms.ChoiceField(choices=SALUTATION_CHOICES)
    contact = forms.CharField()
    day = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Day'
            }), max_value=31)
    month = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Month'
            }), max_value=12)
    year = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Year'
            }))


class AddressForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.address = kwargs.pop('instance', None)
        super(AddressForm, self).__init__(*args, **kwargs)
        if self.address is not None:
            self.fields['address1'].initial = self.address.address1
            self.fields['address2'].initial = self.address.address2
            self.fields['city'].initial = self.address.city
            self.fields['country'].initial = self.address.country
            self.fields['state'].initial = self.address.state
            self.fields['zip_code'].initial = self.address.zip_code
            self.fields['postal_code'].initial = self.address.postal_code
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    address1 = forms.CharField(max_length=100)
    address2 = forms.IntegerField()
    city = forms.CharField(max_length=50)
    country = forms.CharField(max_length=50)
    VIC = 'VIC'
    WA = 'WA'
    TAS = 'TAS'
    QLD = 'QLD'
    NT = 'NT'
    SA = 'SA'
    NSW = 'NSW'
    ACT = 'ACT'
    STATE_CHOICES = (
        (VIC,  'Victoria'),
        (WA,  'Western Australia'),
        (TAS,  'Tasmania'),
        (QLD,  'Queensland'),
        (NT,  'Northern Territory'),
        (SA,  'South Australia'),
        (NSW,  'New South Wales'),
        (ACT,  'Australian Capital Territory'),
    )
    state = forms.ChoiceField(choices=STATE_CHOICES)
    zip_code = forms.IntegerField()
    postal_code = forms.IntegerField()


class PaymentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.payment = kwargs.pop('instance', None)
        super(PaymentForm, self).__init__(*args, **kwargs)
        if self.payment is not None:
            self.fields['pay_type'].initial = self.payment.pay_type
            self.fields['cc_number'].initial = self.payment.cc_number
            self.fields['cc_expiry'].initial = self.payment.cc_expiry
            self.fields['cc_code'].initial = self.payment.cc_code
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    CARD = 'CARD'
    MANUAL = 'MANUAL'
    PAY_TYPES = (
        (CARD, 'Card'),
        (MANUAL, 'Manual'),
    )
    pay_type = forms.ChoiceField(choices=PAY_TYPES)
    cc_number = CardNumberField(label='Card Number')
    cc_expiry = CardExpiryField(label='Expiration Date')
    cc_code = SecurityCodeField(label='CVV/CVC')


class ProxyListForm(forms.Form):
    name = forms.CharField(max_length=50)


class ProxyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProxyForm, self).__init__(*args, **kwargs)
        self.fields['proxy_list'].queryset = ProxyList.objects.filter(user=self.request.user)

    ip_address = forms.GenericIPAddressField()
    port = forms.IntegerField()
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50)
    LOCKED = 'UNLOCKED'
    UNLOCKED = 'UNLOCKED'
    STATUS_TYPES = (
        (LOCKED, 'Locked'),
        (UNLOCKED, 'Unlocked'),
    )
    status = forms.ChoiceField(choices=STATUS_TYPES)
    proxy_list = forms.ModelChoiceField(queryset=None)
