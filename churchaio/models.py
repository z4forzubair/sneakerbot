from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField


# Create your models here.


MALE = 'MALE'
FEMALE = 'FEMALE'
UNKNOWN = 'UNKNOWN'
SEX_TYPES = (
    (MALE, 'MALE'),
    (FEMALE, 'FEMALE'),
    (UNKNOWN, 'UNKNOWN'),
)

JAN = 1
FEB = 2
MAR = 3
APR = 4
MAY = 5
JUN = 6
JUL = 7
AUG = 8
SEP = 9
OCT = 10
NOV = 11
DEC = 12
MONTHS_LIST = (
    (JAN, 'Jan'),
    (FEB, 'Feb'),
    (MAR, 'Mar'),
    (APR, 'Apr'),
    (MAY, 'May'),
    (JUN, 'Jun'),
    (JUL, 'Jul'),
    (AUG, 'Aug'),
    (SEP, 'Sep'),
    (OCT, 'Oct'),
    (NOV, 'Nov'),
    (DEC, 'Dec'),
)

CARD = 'CARD'
MANUAL = 'MANUAL'
PAY_TYPES = (
    (CARD, 'CARD'),
    (MANUAL, 'MANUAL'),
)

LOCKED = 'LOCKED'
UNLOCKED = 'UNLOCKED'
STATUS_TYPES = (
    (LOCKED, 'LOCKED'),
    (UNLOCKED, 'UNLOCKED'),
)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expiry_date = models.DateField()
    renew_count = models.IntegerField(default=0)
    sex = models.CharField(
        max_length=8,
        choices=SEX_TYPES,
        default=UNKNOWN,
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

    class Meta:
        unique_together = ('user', 'name',)


class Proxy(models.Model):
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=50)  # , unique=False
    password = models.CharField(max_length=50)
    status = models.CharField(
        max_length=9,
        choices=STATUS_TYPES,
        blank=True,
        null=True
    )
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    MR = 'MR'
    MS = 'MS'
    SALUTATION_CHOICES = (
        (MR, 'MR'),
        (MS, 'MS'),
    )
    salutation = models.CharField(
        max_length=7,
        choices=SALUTATION_CHOICES,
    )
    contact = PhoneNumberField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name',)


class Address(models.Model):
    address1 = models.CharField(max_length=100)
    address2 = models.IntegerField()
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)     # to be automated/make list
    zip_code = models.IntegerField()
    postal_code = models.IntegerField()
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    pay_type = models.CharField(
        max_length=7,
        choices=PAY_TYPES,
        default=CARD,
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
    sku_link = models.URLField(max_length=120)      # db_index???
    task_count = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.SET_NULL, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
