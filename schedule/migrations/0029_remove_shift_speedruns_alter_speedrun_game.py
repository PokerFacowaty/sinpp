# Generated by Django 4.2.2 on 2023-11-05 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0028_remove_role_type_remove_role_visibility'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shift',
            name='SPEEDRUNS',
        ),
        migrations.AlterField(
            model_name='speedrun',
            name='GAME',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
