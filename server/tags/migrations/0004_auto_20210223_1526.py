# Generated by Django 3.1.1 on 2021-02-23 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0003_auto_20210223_0555'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tagcategory',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='tag',
            name='order',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
