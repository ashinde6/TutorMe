# Generated by Django 4.1.7 on 2023-04-21 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_me', '0023_friendrequest_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='booking',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tutor_me.booking'),
        ),
    ]
