# Generated by Django 4.2.2 on 2023-08-11 05:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0013_remove_role_volunteers'),
    ]

    operations = [
        migrations.AddField(
            model_name='intermission',
            name='ROOM',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.room'),
        ),
        migrations.AddField(
            model_name='shift',
            name='ROOM',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.room'),
        ),
    ]