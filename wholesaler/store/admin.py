from django.contrib import admin
from .models import Store, Seller, Buyer, Product, ProductImage, Branch, Category,Cart, CartItem,Order,OrderItem
from django.utils.html import format_html


class StoreAdmin(admin.ModelAdmin):
    list_display = ['id', 'store_name', 'text', 'created_at']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

class SellerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'gst_number', 'phone_number')

class BuyerAdmin(admin.ModelAdmin):
    list_display = ('user',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'store', 'product_id', 'price', 'stock_status')

    def thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:8px;" />', first_image.image.url)
        return "(No Image)"

    thumbnail.short_description = 'Image'

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

# Register models with error handling to avoid duplicate registration
for model, admin_class in [
    (Store, StoreAdmin),
    (Seller, SellerAdmin),
    (Buyer, BuyerAdmin),
    (Product, ProductAdmin),
    (ProductImage, ProductImageAdmin),
]:
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass  # Ignore if already registered

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state']


admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
