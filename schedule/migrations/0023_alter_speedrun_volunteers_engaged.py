# Generated by Django 4.2.2 on 2023-10-23 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0022_alter_speedrun_volunteers_engaged'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speedrun',
            name='VOLUNTEERS_ENGAGED',
            field=models.ManyToManyField(related_name='SPEEDRUNS_ENGAGED_IN', to='schedule.person'),
        ),
    ]
