# Generated by Django 4.2.2 on 2023-09-02 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0019_room_slug_alter_event_short_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='SLUG',
            field=models.SlugField(max_length=25, unique=True),
        ),
    ]
