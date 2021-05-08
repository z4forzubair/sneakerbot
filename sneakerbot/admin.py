from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(Profile)
admin.site.register(ProxyList)
admin.site.register(Proxy)
admin.site.register(Task)
admin.site.register(Account)
admin.site.register(Address)
admin.site.register(Payment)
