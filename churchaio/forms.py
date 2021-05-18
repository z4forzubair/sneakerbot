from django import forms

from churchaio.models import *
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField


class TaskForm(forms.Form):
    # def __init__(self, *args, **kwargs):
    #     self.user = kwargs.pop('user', None)
    #     super(UserForm, self).__init__(*args, **kwargs)
    store_name = forms.CharField(max_length=50)
    shoe_size = forms.IntegerField()  # to show random
    sku_link = forms.URLField(max_length=120)
    task_count = forms.IntegerField()
    # user = forms.ForeignKey(User, on_delete=models.CASCADE)   # it will be current user
    proxy_list = forms.ModelChoiceField(queryset=ProxyList.objects.all())
    profile = forms.ModelChoiceField(queryset=Profile.objects.all())


class ProfileForm(forms.Form):
    name = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    DUMMY = '---------'
    MR = 'MR'
    MS = 'MS'
    SALUTATION_CHOICES = (
        (DUMMY, '---------'),
        (MR, 'MR'),
        (MS, 'MS'),
    )
    salutation = forms.TypedChoiceField(choices=SALUTATION_CHOICES, coerce=DUMMY)
    contact = forms.CharField()


class PaymentForm(forms.Form):
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
    profile = forms.ModelChoiceField(queryset=Profile.objects.all())


class AddressForm(forms.Form):
    address1 = forms.CharField(max_length=100)
    address2 = forms.IntegerField()
    city = forms.CharField(max_length=50)
    country = forms.CharField(max_length=50)
    state = forms.CharField(max_length=50)  # to be automated/insert list of states
    zip_code = forms.IntegerField()
    postal_code = forms.IntegerField()
    profile = forms.ModelChoiceField(queryset=Profile.objects.all())


class ProxyListForm(forms.Form):
    name = forms.CharField(max_length=50)


class ProxyForm(forms.Form):
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
    proxy_list = forms.ModelChoiceField(queryset=ProxyList.objects.all())
