# Generated by Django 4.2.4 on 2024-08-13 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_alter_orderhistory_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderhistory',
            name='order_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderhistory',
            name='status',
            field=models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Delivered', 'Delivered')], max_length=255, null=True),
        ),
    ]
