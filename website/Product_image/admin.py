from django.contrib import admin
from .models import FullShop,ContactMessage


class FullShopAdminFilter(admin.ModelAdmin):
    list_filter = ["type"]
# Register your models here.
admin.site.register(FullShop,FullShopAdminFilter)
admin.site.register(ContactMessage)

