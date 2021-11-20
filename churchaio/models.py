from creditcards.models import CardNumberField, CardExpiryField, SecurityCodeField
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    expiry_date = models.DateField()
    renew_count = models.IntegerField(null=True, blank=True, default=0)

    class SEX(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        UNKNOWN = 'UNKNOWN', _('Unknown')

    sex = models.CharField(
        max_length=8,
        choices=SEX.choices,
        default=SEX.UNKNOWN
    )
    phone_number = PhoneNumberField()
    complete_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Picture(models.Model):
    picture = models.ImageField(null=True, blank=True, upload_to='img/%y')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Configuration(models.Model):
    timeout = models.PositiveSmallIntegerField()
    retry = models.PositiveIntegerField()
    monitor = models.PositiveIntegerField()
    sleep = models.PositiveSmallIntegerField()
    # may be in separate Notification table
    # notifications = models.BooleanField(default=True)
    # sounds = models.BooleanField(default=True)
    # captcha = models.BooleanField(default=True)
    webhook = models.URLField(max_length=200, null=True, blank=True)
    auto_solve = models.URLField(max_length=200, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


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
    ip_address = models.CharField(max_length=50)
    port = models.CharField(max_length=5)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)

    class STATUS(models.TextChoices):
        LOCKED = 'LOCKED', _('Locked')
        UNLOCKED = 'UNLOCKED', _('Unlocked')

    status = models.CharField(
        max_length=9,
        choices=STATUS.choices,
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

    class SALUTATION(models.TextChoices):
        MR = 'MR', _('Mr')
        MS = 'MS', _('Ms')

    salutation = models.CharField(
        max_length=7,
        choices=SALUTATION.choices,
    )
    day = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    contact = PhoneNumberField()
    favorite = models.BooleanField(default=False)
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

    class AU_STATES(models.TextChoices):
        VIC = 'VIC', _('VIC')
        WA = 'WA', _('WA')
        TAS = 'TAS', _('TAS')
        QLD = 'QLD', _('QLD')
        NT = 'NT', _('NT')
        SA = 'SA', _('SA')
        NSW = 'NSW', _('NSW')
        ACT = 'ACT', _('ACT')

    state = models.CharField(
        max_length=4,
        choices=AU_STATES.choices,
        default=AU_STATES.VIC,
    )
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
    cc_number = CardNumberField('card number')
    cc_expiry = CardExpiryField('expiration date')
    cc_code = SecurityCodeField('security code')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    class STORE_NAME(models.TextChoices):
        FOOTLOCKER = 'FOOTLOCKER', _('Footlocker')
        JD_SPORTS = 'JD_SPORTS', _('JD_Sports')
        HYPEDC = 'HYPEDC', _('hypedc')
        CULTURE_KINGS = 'CULTURE_KINGS', _('Culture Kings')

    store_name = models.CharField(
        max_length=50,
        choices=STORE_NAME.choices,
        default=STORE_NAME.JD_SPORTS
    )
    shoe_size = models.IntegerField(default=-1)
    sku_link = models.URLField(max_length=200)  # db_index???

    class STATUS(models.TextChoices):
        IMMATURE = 'IMMATURE', _('Immature')
        MATURE = 'MATURE', _('Mature')
        RUNNING = 'RUNNING', _('Running')
        FAILED = 'FAILED', _('Failed')
        COMPLETED = 'COMPLETED', _('Completed')

    status = models.CharField(
        max_length=10,
        choices=STATUS.choices,
        default=STATUS.IMMATURE
    )

    celery_id = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # there can be more than one proxy_lists for a task(the mentioned feature might be added later)
    proxy_list = models.ForeignKey(ProxyList, on_delete=models.SET_NULL, blank=True, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['store_name', 'shoe_size', 'sku_link', 'proxy_list', 'profile']


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'first_name', 'last_name', 'email', 'salutation', 'contact', 'day', 'month', 'year']


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = '__all__'


class ProxyListForm(ModelForm):
    class Meta:
        model = ProxyList
        fields = ['name']


class ConfigurationForm(ModelForm):
    class Meta:
        model = Configuration
        fields = ['monitor', 'timeout', 'retry']


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['sex', 'phone_number']


class PictureForm(ModelForm):
    class Meta:
        model = Picture
        fields = ['picture']
