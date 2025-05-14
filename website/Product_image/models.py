from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from autoslug import AutoSlugField


# Create your models here.

class FullShop(models.Model):
    pchoice = [
        ('Niwar', 'Niwar'),
        ('Cow', 'Cow Care'),
        ('Dog', 'Dog Care'),
        ('Horse', 'Horse Care'),
        ('AG', 'Agriculture Tools'),
        ('HT', 'Hardware Tools'),
        ('Rope', 'Ropes'),
        ('PM', 'Packing Items'),
        ('Hatha', 'Hatha'),
        ('Home', 'House Holds'),
    ]

    STOCK_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Out of Stock', 'Out of Stock'),
    ]

    name = models.CharField(max_length=50)
    image = models.ImageField()
    datetime = models.DateTimeField(default=timezone.now)
    type = models.CharField(choices=pchoice, max_length=20)
    brief = HTMLField(default='')
    description = HTMLField(default='')
    stock_status = models.CharField(choices=STOCK_STATUS_CHOICES, max_length=20, default='Available')

    slug = AutoSlugField(populate_from='name', unique=True, null=True, default=None)


    def __str__(self):
        return f"{self.name} - {self.stock_status}"

    class Meta:
        verbose_name_plural = "FullShop"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)