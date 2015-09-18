# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expired', models.BooleanField(default=False)),
                ('key', models.CharField(max_length=200)),
                ('notified_success', models.BooleanField(default=False)),
                ('used', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('color', models.CharField(max_length=200, choices=[(b'danger', b'danger'), (b'info', b'info'), (b'success', b'success'), (b'warning', b'warning')])),
                ('permanent', models.BooleanField()),
                ('text', models.CharField(max_length=200)),
                ('user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=200, null=True, blank=True)),
                ('entered', models.DateTimeField(auto_now_add=True)),
                ('language', models.CharField(max_length=2)),
            ],
            options={
                'ordering': ['alias'],
            },
        ),
        migrations.CreateModel(
            name='AliasPlace',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.ForeignKey(to='appfd.Alias')),
            ],
        ),
        migrations.CreateModel(
            name='Calls',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('total', models.IntegerField(default=0)),
                ('service', models.CharField(max_length=200, choices=[(b'gt', b'Google Translate API')])),
            ],
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.EmailField(max_length=254, null=True, blank=True)),
                ('entered', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParentChild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('admin_level', models.IntegerField(null=True, blank=True)),
                ('area_sqkm', models.IntegerField(null=True, blank=True)),
                ('district_num', models.IntegerField(null=True, blank=True)),
                ('fips', models.IntegerField(null=True, blank=True)),
                ('geonameid', models.IntegerField(null=True, blank=True)),
                ('mls', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326, null=True, blank=True)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, null=True, blank=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('note', models.CharField(max_length=200, null=True, blank=True)),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('population', models.BigIntegerField(null=True, blank=True)),
                ('pcode', models.CharField(max_length=200, null=True, blank=True)),
                ('skeleton', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326, null=True, blank=True)),
                ('timezone', models.CharField(max_length=200, null=True, blank=True)),
                ('aliases', models.ManyToManyField(related_name='place_from_placealias+', through='appfd.AliasPlace', to='appfd.Alias')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('pic', models.ImageField(null=True, upload_to=b'images/topicareas', blank=True)),
                ('position', models.CharField(max_length=200, null=True, blank=True)),
                ('twitter', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Translator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='parentchild',
            name='child',
            field=models.ForeignKey(related_name='subplace', to='appfd.Place'),
        ),
        migrations.AddField(
            model_name='parentchild',
            name='parent',
            field=models.ForeignKey(related_name='parentplace', to='appfd.Place'),
        ),
        migrations.AddField(
            model_name='aliasplace',
            name='place',
            field=models.ForeignKey(to='appfd.Place'),
        ),
        migrations.AlterUniqueTogether(
            name='parentchild',
            unique_together=set([('parent', 'child')]),
        ),
        migrations.AlterUniqueTogether(
            name='aliasplace',
            unique_together=set([('alias', 'place')]),
        ),
    ]
