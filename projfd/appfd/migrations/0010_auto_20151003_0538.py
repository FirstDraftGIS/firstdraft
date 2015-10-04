# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0009_alternatename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alias',
            name='entered',
        ),
        migrations.AlterField(
            model_name='alias',
            name='language',
            field=models.CharField(max_length=7, null=True, blank=True),
        ),
    ]
