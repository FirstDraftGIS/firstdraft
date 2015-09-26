# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0004_auto_20150921_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='country_code',
            field=models.CharField(db_index=True, max_length=2, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(db_index=True, max_length=200, null=True, blank=True),
        ),
    ]
