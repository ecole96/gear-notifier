# Generated by Django 3.0.5 on 2020-08-26 22:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0002_misc'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name': 'Match', 'verbose_name_plural': 'Matches'},
        ),
        migrations.AlterModelOptions(
            name='misc',
            options={'verbose_name': 'Misc', 'verbose_name_plural': 'Misc'},
        ),
    ]
