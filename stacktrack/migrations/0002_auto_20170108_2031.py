# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-08 20:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stacktrack', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fineness',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('multiplier', models.FloatField(default=1.0)),
                ('friendly_name', models.CharField(max_length=80)),
            ],
            options={
                'verbose_name_plural': 'finenesses',
            },
        ),
        migrations.AlterField(
            model_name='greeting',
            name='when',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date created'),
        ),
    ]
