# Generated by Django 5.2 on 2025-04-15 06:12

import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Product_image', '0002_productcatagories_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcatagories',
            name='features',
            field=models.TextField(blank=True, help_text='Comma-separated values for product features'),
        ),
        migrations.AlterField(
            model_name='productcatagories',
            name='description',
            field=tinymce.models.HTMLField(default=''),
        ),
        migrations.AlterField(
            model_name='productcatagories',
            name='type',
            field=models.CharField(choices=[('Niwar', 'Niwar'), ('Cow', 'Cow'), ('AG', 'Agriculture Tools'), ('HT', 'Hardware Tools')], max_length=50),
        ),
    ]
