# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_rename_status_types'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='allocation',
            unique_together=set([]),
        ),
    ]