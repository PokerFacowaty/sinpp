# Generated by Django 4.2.2 on 2023-06-26 22:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_alter_person_roles_remove_shift_volunteer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='TIME_SAFETY_MARGIN',
            field=models.DurationField(default=datetime.timedelta(seconds=900)),
        ),
    ]
