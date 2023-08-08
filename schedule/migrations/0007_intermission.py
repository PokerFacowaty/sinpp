# Generated by Django 4.2.2 on 2023-08-08 03:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0006_shift_speedruns'),
    ]

    operations = [
        migrations.CreateModel(
            name='Intermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('START_TIME', models.DateTimeField()),
                ('DURATION', models.DurationField()),
                ('END_TIME', models.DateTimeField()),
                ('EVENT', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.event')),
                ('VOLUNTEER_SHIFTS', models.ManyToManyField(related_name='INTERMISSIONS_ENGAGED_IN', to='schedule.person')),
            ],
        ),
    ]