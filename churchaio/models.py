from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.forms import ModelForm
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expiry_date = models.DateField()
    renew_count = models.IntegerField(default=0)

    class SEX(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        UNKNOWN = 'UNKNOWN', _('Unknown')

    sex = models.CharField(
        max_length=8,
        choices=SEX.choices,
        default=SEX.UNKNOWN
    )
    photo = models.ImageField(upload_to='media/')
    phone_number = PhoneNumberField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list


class ProxyList(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name',)


class Proxy(models.Model):
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=50)  # , unique=False
    password = models.CharField(max_length=50)

    class STATUS(models.TextChoices):
        LOCKED = 'LOCKED', _('Locked')
        UNLOCKED = 'UNLOCKED', _('Unlocked')

    status = models.CharField(  # should have a default unlocked value
        max_length=9,
        choices=STATUS.choices,
        blank=True,
        null=True
    )
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return f'{self.ip_address} {self.port}'


class Profile(models.Model):
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

    class SALUTATION(models.TextChoices):
        MR = 'MR', _('Mr')
        MS = 'MS', _('Ms')

    salutation = models.CharField(
        max_length=7,
        choices=SALUTATION.choices,
    )
    contact = PhoneNumberField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name',)


class Address(models.Model):
    address1 = models.CharField(max_length=100)
    address2 = models.IntegerField()
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)  # to be automated/make list
    zip_code = models.IntegerField()
    postal_code = models.IntegerField()
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    class PAY(models.TextChoices):
        CARD = 'CARD', _('Card')
        MANUAL = 'MANUAL', _('Manual')

    pay_type = models.CharField(
        max_length=7,
        choices=PAY.choices,
        default=PAY.CARD,
    )
    cc_number = CardNumberField('card number', null=True, blank=True)
    cc_expiry = CardExpiryField('expiration date', null=True, blank=True)
    cc_code = SecurityCodeField('security code', null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    store_name = models.CharField(max_length=50)
    shoe_size = models.IntegerField(default=-1)
    sku_link = models.URLField(max_length=120)  # db_index???
    task_count = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.SET_NULL, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['store_name', 'shoe_size', 'sku_link', 'task_count', 'proxy_list', 'profile']


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'first_name', 'last_name', 'email', 'salutation', 'contact']


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = '__all__'


class ProxyListForm(ModelForm):
    class Meta:
        model = ProxyList
        fields = ['name']


class ProxyForm(ModelForm):
    class Meta:
        model = Proxy
        fields = '__all__'
