# Generated by Django 3.0.4 on 2020-03-24 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='node',
            old_name='port',
            new_name='PORT',
        ),
        migrations.AddField(
            model_name='node',
            name='status',
            field=models.TextField(default='Online', max_length=7),
            preserve_default=False,
        ),
    ]
