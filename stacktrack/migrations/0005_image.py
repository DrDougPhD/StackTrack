# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-08 23:06
from __future__ import unicode_literals

import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stacktrack', '0004_auto_20170108_2110'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('is_obverse', models.BooleanField(choices=[(True, 'obverse'), (False, 'reverse')], default=True)),
                ('ingot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stacktrack.Ingot')),
            ],
        ),
    ]