# Generated by Django 5.2 on 2025-04-18 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product_image', '0017_alter_fullshop_brief'),
    ]

    operations = [
        migrations.AddField(
            model_name='fullshop',
            name='price',
            field=models.IntegerField(default=123),
            preserve_default=False,
        ),
    ]
