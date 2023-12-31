# Generated by Django 4.0.3 on 2022-04-15 20:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_remove_category_listings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='listing',
            options={'ordering': ['pk']},
        ),
        migrations.AddField(
            model_name='listing',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to='auctions.category'),
        ),
    ]
