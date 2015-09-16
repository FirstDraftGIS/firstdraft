# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0004_geoname'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GeoName',
        ),
    ]
