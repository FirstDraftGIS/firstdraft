# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appfd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentChild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('child', models.ForeignKey(related_name='subplace', to='appfd.Place')),
                ('parent', models.ForeignKey(related_name='parentplace', to='appfd.Place')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='parentchild',
            unique_together=set([('parent', 'child')]),
        ),
    ]
