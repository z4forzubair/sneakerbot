from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models


# Create your models here.


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expiry_date = models.DateField()
    renew_count = models.IntegerField(default=0)
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    UNKNOWN = 'UNKNOWN'
    TYPES_CHOICES = (
        (MALE, 'MALE'),
        (FEMALE, 'FEMALE'),
        (UNKNOWN, 'UNKNOWN'),
    )
    sex = models.CharField(
        max_length=7,
        choices=TYPES_CHOICES,
        default=UNKNOWN,
    )
    photo = models.ImageField(upload_to='media/')
    phone_number = PhoneNumberField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    # phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list


class ProxyList(models.Model):
    name = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name',)


class Proxy(models.Model):
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=20)  # , unique=False
    password = models.CharField(max_length=20)
    store = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    name = models.CharField(max_length=20)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
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
    address1 = models.CharField(max_length=30)
    address2 = models.IntegerField()
    city = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip_code = models.IntegerField()
    postal_code = models.IntegerField()
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payment(models.Model):
    CARD = 'CARD'
    MANUAL = 'MANUAL'
    TYPES_CHOICES = (
        (CARD, 'CARD'),
        (MANUAL, 'MANUAL'),
    )
    sex = models.CharField(
        max_length=6,
        choices=TYPES_CHOICES,
        default=CARD,
    )
    card_number = models.IntegerRangeField(max_value=9999999999999999)  # left for now IntegerRangeField, may be modified
    cvv = models.IntegerRangeField(max_value=999)
    expiry_month = models.DateTimeField()
    expiry_year = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    store_name = models.CharField(max_length=20)
    shoe_size = models.IntegerField(default=-1)
    sku_link = models.URLField(max_length=120)      # db_index???
    task_count = models.IntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.SET_NULL, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
