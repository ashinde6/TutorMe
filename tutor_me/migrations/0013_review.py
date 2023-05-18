# Generated by Django 4.1.7 on 2023-04-12 22:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_me', '0012_alter_time_range_end_alter_time_range_start'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('commenter', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='commenter', to='tutor_me.tm_user')),
                ('target', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='target', to='tutor_me.tm_user')),
            ],
        ),
    ]