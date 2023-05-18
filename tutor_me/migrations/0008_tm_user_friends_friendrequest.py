# Generated by Django 4.1.6 on 2023-04-01 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_me', '0007_tm_user_age_tm_user_hourly_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='tm_user',
            name='friends',
            field=models.ManyToManyField(blank=True, to='tutor_me.tm_user'),
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to='tutor_me.tm_user')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_user', to='tutor_me.tm_user')),
            ],
        ),
    ]