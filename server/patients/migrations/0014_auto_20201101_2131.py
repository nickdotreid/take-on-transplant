# Generated by Django 3.1.1 on 2020-11-01 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0013_auto_20201101_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientattribute',
            name='order',
        ),
        migrations.RemoveField(
            model_name='patientattribute',
            name='published',
        ),
    ]
