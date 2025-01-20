# Generated by Django 5.0.6 on 2025-01-05 06:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('events', '0003_remove_postfeedback_post_postfeedback_content_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postfeedback',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
    ]
