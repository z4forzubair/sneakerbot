from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Login(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cookie = models.CharField(max_length=50)
    pc = models.BooleanField(default=False)
    mobile = models.BooleanField(default=False)
    tablet = models.BooleanField(default=False)
    is_logged_in = models.BooleanField(default=False)

    # is_logged_in currently useless, but similar variable for each device type can be used

    def __str__(self):
        return self.user.username
