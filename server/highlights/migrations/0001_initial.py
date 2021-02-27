# Generated by Django 3.1.1 on 2021-02-27 00:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('study_sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HighlightedContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_id', models.CharField(max_length=100)),
                ('content', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Highlight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('content', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='highlights.highlightedcontent')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='study_sessions.studysession')),
            ],
        ),
    ]
