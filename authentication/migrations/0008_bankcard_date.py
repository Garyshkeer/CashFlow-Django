# Generated by Django 4.0.1 on 2022-05-05 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_remove_outflow_billet_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankcard',
            name='date',
            field=models.DateTimeField(null=True),
        ),
    ]
