# Generated by Django 3.1.1 on 2021-02-26 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0009_auto_20210226_0002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ['order', 'title']},
        ),
    ]
