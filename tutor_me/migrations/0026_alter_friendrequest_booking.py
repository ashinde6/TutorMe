# Generated by Django 4.1.7 on 2023-04-21 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_me', '0025_alter_booking_friend_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='booking',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tutor_me.booking'),
        ),
    ]
