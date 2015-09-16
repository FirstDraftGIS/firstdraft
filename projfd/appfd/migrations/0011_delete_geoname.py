# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0010_auto_20150914_0429'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GeoName',
        ),
    ]
