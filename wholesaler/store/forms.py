from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Store, Product, Branch, BranchUser, ProductImage,Order

# ---------------------------
# Seller, Buyer, BranchUser Registration Forms
# ---------------------------

class SellerRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    company_name = forms.CharField(max_length=100)
    gst_number = forms.CharField(max_length=15)
    phone_number = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            from .models import Seller
            Seller.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                gst_number=self.cleaned_data['gst_number'],
                phone_number=self.cleaned_data['phone_number'],
                role=0  # Seller
            )
        return user

class BuyerRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=255)
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            from .models import Buyer
            Buyer.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone_number=self.cleaned_data['phone_number'],
                role=2  # Buyer
            )
        return user

class BranchUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)


    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.role = 1  # BranchUser
        if commit:
            instance.save()
        return instance

# ---------------------------
# Store Form
# ---------------------------

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['text', 'photo', 'store_name']

# ---------------------------
# Product Form
# ---------------------------

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock_quantity', 'stock_status', 'branch', 'description']
        labels = {
            'stock_quantity': 'Stock Quantity (Units)',
        }

# ---------------------------
# Product Images Formset
# ---------------------------

from django.forms import modelformset_factory
ProductImageFormSet = modelformset_factory(ProductImage, fields=('image',), extra=3)

# ---------------------------
# Branch Form
# ---------------------------

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'address', 'city', 'state', 'pincode']



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'phone', 'payment_method']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'payment_method': forms.RadioSelect()
        }