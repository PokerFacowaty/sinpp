# Generated by Django 4.2.2 on 2023-11-04 00:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0023_alter_speedrun_volunteers_engaged'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='SHORT_TITLE',
            new_name='SLUG',
        ),
        migrations.RenameField(
            model_name='intermission',
            old_name='END_TIME',
            new_name='END_DATE_TIME',
        ),
        migrations.RenameField(
            model_name='intermission',
            old_name='START_TIME',
            new_name='START_DATE_TIME',
        ),
        migrations.RenameField(
            model_name='speedrun',
            old_name='END_TIME',
            new_name='END_DATE_TIME',
        ),
        migrations.RenameField(
            model_name='speedrun',
            old_name='START_TIME',
            new_name='START_DATE_TIME',
        ),
    ]
