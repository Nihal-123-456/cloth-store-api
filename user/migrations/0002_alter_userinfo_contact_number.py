# Generated by Django 4.2.4 on 2024-04-27 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='contact_number',
            field=models.IntegerField(),
        ),
    ]
