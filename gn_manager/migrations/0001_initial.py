# Generated by Django 3.0.5 on 2020-06-28 02:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.CharField(max_length=250)),
                ('min_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('max_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('cl', models.BooleanField(default=True, verbose_name='Craigslist')),
                ('gc', models.BooleanField(default=True, verbose_name='Guitar Center')),
                ('rv', models.BooleanField(default=True, verbose_name='Reverb')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]