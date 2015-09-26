# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0006_auto_20150922_0211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='fips',
            field=models.IntegerField(db_index=True, null=True, blank=True),
        ),
    ]
