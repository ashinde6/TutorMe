# Generated by Django 4.1.7 on 2023-04-12 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_me', '0016_alter_review_target'),
    ]

    operations = [
        migrations.AddField(
            model_name='tm_user',
            name='reviews',
            field=models.ManyToManyField(blank=True, to='tutor_me.review'),
        ),
    ]