# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='country_code',
            field=models.CharField(max_length=2, null=True, blank=True),
        ),
    ]
