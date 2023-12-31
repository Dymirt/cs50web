# Generated by Django 4.0 on 2022-12-14 21:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_user_influencers_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(related_name='post_liked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='influencers',
            field=models.ManyToManyField(related_name='subscribers', to=settings.AUTH_USER_MODEL),
        ),
    ]
