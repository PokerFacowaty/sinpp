# Generated by Django 4.2.2 on 2023-07-04 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_event_time_safety_margin'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='SPEEDRUNS',
            field=models.ManyToManyField(blank=True, to='schedule.speedrun'),
        ),
    ]
