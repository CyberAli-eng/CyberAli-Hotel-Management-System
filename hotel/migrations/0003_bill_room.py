# Generated by Django 5.2 on 2025-05-14 22:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0002_rename_check_in_customer_check_in_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='room',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='hotel.room'),
            preserve_default=False,
        ),
    ]
