# Generated by Django 3.0.4 on 2020-03-24 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0008_auto_20200324_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='tr',
        ),
        migrations.AddField(
            model_name='node',
            name='node_id',
            field=models.IntegerField(null=True),
        ),
    ]
