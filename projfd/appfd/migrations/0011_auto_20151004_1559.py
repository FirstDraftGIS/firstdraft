# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0010_auto_20151003_0538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alias',
            name='alias',
            field=models.CharField(db_index=True, max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='alias',
            name='language',
            field=models.CharField(db_index=True, max_length=7, null=True, blank=True),
        ),
    ]
