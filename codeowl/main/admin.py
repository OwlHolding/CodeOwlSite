from django.contrib import admin
from .models import UserUpgrade, BlockedList

admin.site.register(UserUpgrade)
admin.site.register(BlockedList)


